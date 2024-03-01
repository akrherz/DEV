"""Find closest in time warning for a watch."""

import datetime
from datetime import timezone

import numpy as np

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def check_negative(df, pgconn):
    """Check for false positives."""
    df2 = df[df["lead"] < 0]
    cursor = pgconn.cursor()
    for idx, row in df2.iterrows():
        cursor.execute(
            "SELECT issue from warnings where ugc in %s and "
            "phenomena in ('SV', 'TO') and significance = 'A' and "
            "issue <= %s and expire > %s",
            (tuple(row["ugcs"]), row["issue"], row["issue"]),
        )
        if cursor.rowcount > 0:
            df.at[idx, "lead"] = np.nan

    cursor.close()


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis")

    watches = read_sql(
        """
    SELECT ugc, wfo, eventid, phenomena,
    issue at time zone 'UTC' as issue,
    expire at time zone 'UTC' as expire,
    extract(year from issue)::int as year from warnings
    where phenomena in ('TO', 'SV') and significance = 'A' and
    issue > '2005-10-01' ORDER by year, eventid
    """,
        pgconn,
        index_col=None,
    )
    watches["issue"] = watches["issue"].dt.tz_localize(timezone.utc)
    watches["expire"] = watches["expire"].dt.tz_localize(timezone.utc)
    data = []
    for (year, eventid), gdf in watches.groupby(["year", "eventid"]):
        ugcs = gdf["ugc"].tolist()
        # Look for any warnings that are 1 hour prior or to expiration
        issue = gdf["issue"].min()
        sts = issue - datetime.timedelta(hours=2)
        ets = gdf["expire"].max()
        warnings = read_sql(
            "SELECT wfo, eventid, phenomena, array_agg(ugc) as ugcs, "
            "issue at time zone 'UTC' as issue from warnings "
            "where phenomena in ('SV', 'TO') and significance = 'W' and "
            "ugc in %s and issue >= %s and issue < %s "
            "GROUP by wfo, eventid, phenomena, issue "
            "ORDER by issue ASC",
            pgconn,
            params=(tuple(ugcs), sts, ets),
        )
        if warnings.empty:
            print(f"Skunked? {year} {eventid}")
            minlead = "M"
            warnbefore = "M"
            warnafter = "M"
        else:
            warnings["issue"] = warnings["issue"].dt.tz_localize(timezone.utc)
            warnings["lead"] = (
                warnings["issue"] - issue
            ).dt.total_seconds() / 60.0
            check_negative(warnings, pgconn)
            warnings = warnings[~pd.isna(warnings["lead"])]
            minlead = warnings["lead"].min()
            warnbefore = len(warnings[warnings["lead"] <= 0].index)
            warnafter = len(warnings.index) - warnbefore
        data.append(
            {
                "year": year,
                "watchnum": eventid,
                "watchtype": gdf.iloc[0]["phenomena"],
                "issue": issue.strftime("%Y-%m-%d %H:%M"),
                "minlead": minlead,
                "wfos": ",".join(gdf["wfo"].unique().tolist()),
                "warnbefore": warnbefore,
                "warnafter": warnafter,
            }
        )
        print(f"year:{year} eventid:{eventid} minlead:{minlead:.2f}")

    df = pd.DataFrame(data)
    df.to_excel("watch_leadtime_m2_v3.xlsx", index=False)


if __name__ == "__main__":
    main()
