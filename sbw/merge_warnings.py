"""Add warning information to a CSV file."""
import datetime

import numpy as np
from pyiem.util import get_dbconn
import pandas as pd
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    df = pd.read_csv("intensetors.csv")
    # Make valid timestamp for database usage
    df["timestampUTC"] = pd.to_datetime(
        df["date"] + " " + df["CST"], format="%y-%m-%d %H:%M:%S"
    ) + datetime.timedelta(hours=6)
    # Addition columns that we are going to provide
    for colname in [
        "first_motion_drct",
        "first_motion_sknt",
        "first_torwarn_link",
    ]:
        df[colname] = None
    # Get a database connection
    dbconn = get_dbconn("postgis")
    # Loop over the tors
    for idx, row in df.iterrows():
        dt = row["timestampUTC"].strftime("%Y-%m-%d %H:%M+00")
        # Find the TORs that intersect in space and time
        sbws = read_sql(
            """
            SELECT wfo, eventid, issue, expire, phenomena, status,
            tml_direction, tml_sknt from sbw
            WHERE ST_Contains(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
            and issue <= %s and expire > %s
            and phenomena in ('TO', 'SV') ORDER by issue ASC
        """,
            dbconn,
            params=(row["slon"], row["slat"], dt, dt),
        )
        if sbws.empty:
            continue
        torwarns = sbws[sbws["phenomena"] == "TO"]
        if not torwarns.empty:
            trow = torwarns.iloc[0]
            df.at[idx, "first_torwarn_link"] = (
                "https://mesonet.agron.iastate.edu/vtec/f/%s"
                "-O-NEW-K%s-TO-W-%04i"
            ) % (trow["issue"].year, trow["wfo"], trow["eventid"])
        else:
            trow = sbws.iloc[0]
        df.at[idx, "first_motion_drct"] = trow["tml_direction"]
        df.at[idx, "first_motion_sknt"] = trow["tml_sknt"]

    df.to_csv("results.csv")


if __name__ == "__main__":
    main()
