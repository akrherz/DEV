"""Sometimes stations had varying reset times.

See akrherz/iem#104
"""

import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_sqlalchemy_conn, get_dbconn, logger

LOG = logger()
ATTR = "METAR_RESET_MINUTE"


def do(asosdb, pgconn, station, minute):
    """Process this network."""
    for year in range(1996, 2023):
        # Look for trouble
        df = pd.read_sql(
            f"""
            select date_trunc('hour', valid) as ts,
            sum(case when report_type = 3 then 1 else 0 end) as routine_hits,
            sum(case when report_type = 4 then 1 else 0 end) as special_hits
            from t{year} WHERE station = %s and valid > '1996-07-01'
            GROUP by ts
            """,
            pgconn,
            params=(station,),
        )
        if len(df.index) < 100:
            continue
        # Require that 90% of hours have hits
        if len(df[df["routine_hits"] == 0].index) < (len(df.index) * 0.1):
            continue
        # Construct a histogram for the station
        df = pd.read_sql(
            f"""
            select extract(minute from valid)::int as minute, count(*)
            from t{year} WHERE station = %s and valid > '1996-07-01'
            GROUP by minute ORDER by count desc
            """,
            pgconn,
            params=(station,),
            index_col="minute",
        )
        newminute = df.index[0]
        LOG.info("Missing  %s[%s] %s->%s", station, minute, year, newminute)
        cursor = asosdb.cursor()
        cursor.execute(
            f"UPDATE t{year} SET report_type = 3 where station = %s and "
            "report_type = 4 and extract(minute from valid) = %s",
            (station, newminute),
        )
        LOG.info("%s %s %s -> 4 to 3", cursor.rowcount, station, year)
        asosdb.commit()


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("mesosite") as conn:
        netdf = pd.read_sql(
            "SELECT id from networks where id ~* '_ASOS'",
            conn,
            index_col=None,
        )
    for network in netdf["id"].values:
        if network.find("__") > -1:
            continue
        nt = NetworkTable(network, only_online=False)
        asosdb = get_dbconn("asos")
        for station in nt.sts:
            minute = nt.sts[station]["attributes"].get(ATTR)
            if minute is None:
                continue
            with get_sqlalchemy_conn("asos") as pgconn:
                do(asosdb, pgconn, station, minute)


if __name__ == "__main__":
    main()
