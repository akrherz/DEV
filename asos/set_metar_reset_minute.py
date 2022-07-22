"""Set the minute at which the METAR *currently* resets.

See akrherz/iem#104
"""

import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_sqlalchemy_conn, get_dbconn, logger

LOG = logger()
ATTR = "METAR_RESET_MINUTE"


def determine_winner(df, station):
    """Who wins?"""
    df["dist"] = df["count"] / df["count"].max()
    if len(df.index) == 1:
        return df.index[0]
    # If the second place is distant
    if df.iloc[1]["dist"] < 0.5:
        return df.index[0]
    possible = df[df["dist"] > 0.9]
    possible = possible[possible.index >= 50].index
    if len(possible) == 1:
        return possible.values[0]
    if 55 in possible.values:
        return 55
    print("Throwing up hands.....")
    print(station)
    print(df)
    print(possible)
    return None


def do(mesosite, iemid, station):
    """Process this network."""
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            "SELECT extract(minute from valid) as minute, count(*) from "
            "t2022 where station = %s and report_type = 2 "
            "GROUP by minute order by count desc",
            conn,
            params=(station,),
            index_col="minute",
        )
    if df.empty:
        LOG.info("No current data found for %s", station)
        return
    minute = determine_winner(df, station)
    if minute is None:
        return
    minute = int(minute)
    LOG.info("%s -> %s", station, minute)
    cursor = mesosite.cursor()
    cursor.execute(
        "INSERT into station_attributes (iemid, attr, value) "
        "VALUES (%s, %s, %s)",
        (iemid, ATTR, minute),
    )
    mesosite.commit()


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("mesosite") as conn:
        netdf = pd.read_sql(
            "SELECT id from networks where id ~* '_ASOS'",
            conn,
            index_col=None,
        )
    for network in netdf["id"].values:
        nt = NetworkTable(network, only_online=False)
        mesosite = get_dbconn("mesosite")
        for station in nt.sts:
            if nt.sts[station]["attributes"].get(ATTR) is not None:
                continue
            do(mesosite, nt.sts[station]["iemid"], station)


if __name__ == "__main__":
    main()
