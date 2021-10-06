"""Debug printout of partitioned table speed within ASOS database"""
import datetime
import sys

from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go"""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    maxt = 0
    for yr in range(1928, datetime.datetime.now().year + 1):
        sts = datetime.datetime.now()
        cursor.execute(
            f"SELECT count(*) from t{yr} WHERE station = %s",
            (argv[1],),
        )
        row = cursor.fetchone()
        ets = datetime.datetime.now()
        secs = (ets - sts).total_seconds()
        print(
            "%s %6i %8.4f%s"
            % (yr, row[0], secs, " <-- " if secs > maxt else "")
        )
        maxt = max([secs, maxt])


if __name__ == "__main__":
    main(sys.argv)
