"""Create intermediate precip file from ASOS hourly data."""

import shutil

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    # scenario = 141
    hucs = [x.strip() for x in open("myhucs.txt")]
    # Figure out the centroid of each
    df = read_sql(
        "SELECT huc_12, st_x(ST_transform(ST_centroid(geom), 4326)) as lon, "
        "st_y(ST_transform(ST_centroid(geom), 4326)) as lat from huc12 where "
        "scenario = 0 and huc_12 in %s",
        get_dbconn("idep"),
        params=(tuple(hucs),),
        index_col="huc_12",
    )
    cursor = get_dbconn("mesosite").cursor()
    done = {}
    for huc_12, row in df.iterrows():
        # Find closest ASOS in iowa
        cursor.execute(
            "SELECT id, iemid, st_distance(geom, "
            "ST_GeomFromEWKT('SRID=4326;POINT(%s %s)')) as dist from stations "
            "where network = 'IA_ASOS' ORDER by dist ASC LIMIT 1",
            (row["lon"], row["lat"]),
        )
        asos, iemid, _dist = cursor.fetchone()
        print(f"{huc_12} -> {asos}")
        if asos in done:
            shutil.copyfile(f"{done[asos]}.csv", f"{huc_12}.csv")
            continue
        # Get the hourly obs
        obs = read_sql(
            "select valid at time zone 'UTC' as utc_valid, phour "
            "from hourly where valid >= '2007-01-01' and valid < '2021-01-01' "
            "and iemid = %s ORDER by valid ASC",
            get_dbconn("iem"),
            params=(iemid,),
            index_col="utc_valid",
        )
        obs = obs.reindex(
            pd.date_range("2007/01/01", "2021/01/01", freq="1H")
        ).fillna(0)
        with open(f"{huc_12}.csv", "w") as fh:
            fh.write("valid,precip_mm\n")
            for idx, row in obs.iterrows():
                fh.write(
                    "%s,%.2f\n"
                    % (idx.strftime("%Y-%m-%d %H:%M"), row["phour"] * 25.4)
                )
        done[asos] = huc_12


if __name__ == "__main__":
    main()
