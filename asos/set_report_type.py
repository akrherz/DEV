"""Set the minute at which the METAR *currently* resets.

See akrherz/iem#104
"""

import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()
ATTR = "METAR_RESET_MINUTE"


def do(asosdb, station, minute):
    """Process this network."""
    for year in range(1996, 2023):
        cursor = asosdb.cursor()
        cursor.execute(
            f"UPDATE t{year} SET report_type = 3 where station = %s and "
            "report_type = 2 and extract(minute from valid) = %s",
            (station, minute),
        )
        LOG.info("%s %s %s -> 3", cursor.rowcount, station, year)
        cursor.execute(
            f"UPDATE t{year} SET report_type = 4 where station = %s and "
            "report_type = 2",
            (station,),
        )
        LOG.info("%s %s %s -> 4", cursor.rowcount, station, year)
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
        nt = NetworkTable(network, only_online=False)
        asosdb = get_dbconn("asos")
        for station in nt.sts:
            minute = nt.sts[station]["attributes"].get(ATTR)
            if minute is None:
                continue
            do(asosdb, station, minute)


if __name__ == "__main__":
    main()
