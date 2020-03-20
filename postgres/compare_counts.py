"""Utility script to compare database counts

    python compare_counts.py <database_name>

Port 5556 is the old, Port 5557 is the new
ssh -L 5556:192.168.1.251:5432 -L 5557:192.168.1.233:5432 mesonet@mesonet
"""
from __future__ import print_function
import sys

from pyiem.util import get_dbconn
import tqdm


def main(argv):
    """Go!"""
    dbname = argv[1]
    oldpg = get_dbconn(dbname, user="mesonet", host="127.0.0.1", port=5556)
    newpg = get_dbconn(dbname, user="mesonet", host="127.0.0.1", port=5557)

    print("running %s..." % (dbname,))
    ocursor = oldpg.cursor()
    ncursor = newpg.cursor()

    tables = []
    ocursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables WHERE table_schema = 'public'
        ORDER BY table_name
    """
    )
    for row in ocursor:
        # skip the agg tables as they are just too massive
        if row[0].startswith("alldata"):
            continue
        tables.append(row[0])

    for table in tqdm.tqdm(tables):
        ocursor.execute("""SELECT count(*) from """ + table)
        ncursor.execute("""SELECT count(*) from """ + table)
        orow = ocursor.fetchone()
        nrow = ncursor.fetchone()
        if orow[0] != nrow[0]:
            print("%s->%s old:%s new:%s" % (dbname, table, orow[0], nrow[0]))


if __name__ == "__main__":
    main(sys.argv)
