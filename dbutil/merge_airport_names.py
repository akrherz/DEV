"""Merge this info."""
import sys

import pandas as pd
from pyiem.util import get_dbconn, logger

LOG = logger()
SRC = (
    "https://raw.githubusercontent.com/jpatokal/openflights/"
    "master/data/airports.dat"
)


def main(argv):
    """Go Main Go."""
    networkin = argv[1]
    df = pd.read_csv(SRC, header=None)

    dbconn = get_dbconn("mesosite")
    cursor = dbconn.cursor()
    cursor2 = dbconn.cursor()
    cursor.execute(
        "SELECT id, name, network from stations where network = %s",
        (networkin,),
    )
    for row in cursor:
        sid = row[0]
        network = row[2]
        df2 = df[df[5] == sid]
        if df2.empty:
            LOG.info("Station %s is unknown in airports.dat", sid)
            continue
        try:
            name = df2.iloc[0][2].replace(" Airport", "").replace(",", " ")
        except Exception as exp:
            LOG.exception(exp)
            continue
        cursor2.execute(
            "UPDATE stations SET name = %s where id = %s and network = %s",
            (name, sid, network),
        )
        LOG.info("%s '%s' -> '%s'", sid, row[1], name)

    cursor2.close()
    dbconn.commit()
    dbconn.close()


if __name__ == "__main__":
    main(sys.argv)
