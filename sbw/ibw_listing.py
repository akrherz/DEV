"""
Wants:
  IBW tags of 2.75" Hail and/or 80+ MPH  (either initial and/or followups)

  - number of reports that verified the criterion
  - initial + followup hail and wind tags
  - where within the warning did the big LSRs happen
"""

# pylint: disable=abstract-class-instantiated
from datetime import timezone

from tqdm import tqdm

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")

    # Get events for consideration
    df = read_sql(
        """
        WITH events as (
            select wfo, phenomena, eventid,
            extract(year from polygon_begin)::numeric as year,
            max(case when status = 'NEW' then hailtag else 0 end)
                as init_hailtag,
            max(case when status = 'NEW' then windtag else 0 end)
                as init_windtag,
            max(case when status = 'NEW' then tml_sknt else 0 end)
                as init_tml_sknt,
            max(tml_sknt) as max_tml_sknt,
            max(hailtag) as max_hailtag,
            max(windtag) as max_windtag from sbw WHERE phenomena = 'SV'
            GROUP by wfo, phenomena, eventid, year)
        SELECT * from events where max_windtag >= 80 or max_tml_sknt >= 50
        ORDER by year, wfo, eventid
    """,
        pgconn,
        index_col=None,
    )
    df["max_hail_report"] = None
    df["max_wind_report"] = None
    df["hail_reports"] = 0
    df["wind_reports"] = 0

    ws = []
    for i, row in tqdm(df.iterrows(), total=len(df.index)):
        # Get the polygon history for this warning
        sbwtable = f"sbw_{row['year']}"
        lsrtable = f"lsrs_{row['year']}"
        warndf = read_sql(
            f"""
        SELECT row_number() over(ORDER by polygon_begin ASC) as sequence,
        wfo, eventid, phenomena,
        extract(year from polygon_begin)::numeric as year,
        polygon_begin at time zone 'UTC' as polygon_begin,
        polygon_end at time zone 'UTC' as polygon_end,
        status, windtag, hailtag, tml_sknt,
        ST_asText(geom) as geomtext from {sbwtable} WHERE wfo = %s
        and eventid = %s and phenomena = %s and significance = %s
        and status != 'EXP' ORDER by polygon_begin
        """,
            pgconn,
            params=(row["wfo"], row["eventid"], row["phenomena"], "W"),
            index_col=None,
        )
        warndf["max_hail_report"] = None
        warndf["max_wind_report"] = None
        warndf["hail_reports"] = 0
        warndf["wind_reports"] = 0
        for j, wrow in warndf.iterrows():
            # Get LSRs
            lsrdf = read_sql(
                f"""
            SELECT distinct city, valid, type, magnitude
            from {lsrtable} WHERE valid >= %s and
            valid < %s and wfo = %s and type in ('H', 'G')
            and ST_Contains(ST_SetSrid(ST_GeometryFromText(%s), 4326), geom)
            """,
                pgconn,
                params=(
                    wrow["polygon_begin"].replace(tzinfo=timezone.utc),
                    wrow["polygon_end"].replace(tzinfo=timezone.utc),
                    row["wfo"],
                    wrow["geomtext"],
                ),
                index_col=None,
            )
            if len(lsrdf.index) == 0:
                continue
            g = lsrdf[lsrdf["type"] == "G"]
            h = lsrdf[lsrdf["type"] == "H"]
            if len(g.index) > 0:
                warndf.at[j, "wind_reports"] = len(g.index)
                warndf.at[j, "max_wind_report"] = g["magnitude"].max()
            if len(h.index) > 0:
                warndf.at[j, "hail_reports"] = len(h.index)
                warndf.at[j, "max_hail_report"] = h["magnitude"].max()
        del warndf["geomtext"]
        ws.append(warndf)
        df.at[i, "wind_reports"] = warndf["wind_reports"].sum()
        df.at[i, "hail_reports"] = warndf["hail_reports"].sum()
        df.at[i, "max_wind_report"] = warndf["max_wind_report"].max()
        df.at[i, "max_hail_report"] = warndf["max_hail_report"].max()

    w = pd.concat(ws)
    with pd.ExcelWriter("ibwlisting.xlsx") as writer:
        df.to_excel(writer, "Overview", index=False)
        w.to_excel(writer, "By Polygon", index=False)


if __name__ == "__main__":
    main()
