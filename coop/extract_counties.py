"""Extraction requested by Maciej"""

import sys

import pandas as pd
from metpy.units import units
from pyiem.util import get_dbconn
from tqdm import tqdm


def dump(pgconn, sid, ncdc81, fips):
    """Go for this sid!"""
    df = pd.read_sql(
        """
        WITH avgs as (
            select to_char(valid, 'mmdd') as sday, high, low, precip
            from ncdc_climate81 where station = %s
        )
        SELECT day,
        o.high as obs_high_c, o.low as obs_low_c,
        (case when o.precip < 0.009 then 0 else o.precip end) as obs_precip_mm,
        c.high as climo_high_c, c.low as climo_low_c,
        c.precip as climo_precip_mm
        from alldata o JOIN avgs c on (o.sday = c.sday)
        WHERE o.station = %s and o.year >= 2006 and o.year < 2020
        ORDER by day ASC
        """,
        pgconn,
        params=(ncdc81, sid),
    )
    if df.empty:
        print(sid)
        print(ncdc81)
        sys.exit()
    for col in ["obs_high_c", "obs_low_c", "climo_high_c", "climo_low_c"]:
        df[col] = (df[col].values * units.degF).to(units.degC).m
    for col in ["obs_precip_mm", "climo_precip_mm"]:
        df[col] = (df[col].values * units.inch).to(units.mm).m
    df["fips"] = fips
    df["iem_station"] = sid
    df["ncdc_station"] = ncdc81
    fn = f"data/{sid[:2]}_{fips}.csv"
    df.to_csv(fn, index=False, float_format="%.2f")


def main(_argv):
    """Do Something"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    pgconn2 = get_dbconn("coop")
    ugcs = pd.read_sql(
        """
        SELECT ugc, ST_X(centroid) as lon, ST_Y(centroid) as lat
        from ugcs where substr(ugc,3,1) = 'C'
        and end_ts is null ORDER by ugc ASC
    """,
        pgconn,
        index_col="ugc",
    )
    ugcs["done"] = 0
    fips = pd.read_excel("/tmp/counties.xlsx", dtype={"Fips": str})
    progress = tqdm(fips.iterrows(), total=len(fips.index))
    for _idx, row in progress:
        ugc = f"{row['ST']}C{row['Fips'][2:]}"
        progress.set_description(ugc)
        if ugcs.at[ugc, "done"] == 1:
            continue
        ugcs.at[ugc, "done"] = 1
        row2 = ugcs.loc[ugc]
        # Get closest climodat site
        cursor.execute(
            """
            SELECT id, ncdc81, ST_Distance(geom,
            ST_SetSRID(ST_GeomFromText('POINT(%s %s)'), 4326))
            from stations where network ~* 'CLIMATE' and
            substr(id, 3, 4) != '0000'
            and substr(id,3,1) != 'C' ORDER by st_distance ASC LIMIT 1
            """,
            (row2["lon"], row2["lat"]),
        )
        (sid, ncdc81, _unused) = cursor.fetchone()
        dump(pgconn2, sid, ncdc81, row["Fips"])


if __name__ == "__main__":
    main(sys.argv)
