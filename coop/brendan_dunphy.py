"""weekly data dump."""

import datetime
import sys

from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()

    sts = datetime.datetime(2016, 2, 1)
    ets = datetime.datetime(2016, 11, 18)
    interval = datetime.timedelta(days=7)

    now = sts
    while now < ets:
        e = now + interval
        sql = """SELECT avg(high) as h, avg(low) as l, sum(precip) as p
            from alldata_ia WHERe station = '%s' and day >= '%s' and day < '%s'
            """ % (
            sys.argv[1],
            now.strftime("%Y-%m-%d"),
            e.strftime("%Y-%m-%d"),
        )
        cursor.execute(sql)
        row = cursor.fetchone()
        print(
            "%s,%.1f,%.1f,%.2f"
            % (now.strftime("%Y-%m-%d"), row[0], row[1], row[2])
        )
        now += interval


if __name__ == "__main__":
    main()
