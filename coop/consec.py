"""consec days"""
from __future__ import print_function

from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn('coop', user='nobody')
    cursor = pgconn.cursor()
    cursor.execute("""
    WITH climo as (
        select sday, avg(high) from alldata_ia where station = 'IA2203'
        GROUP by sday)
    select day, high, c.avg from alldata_ia a JOIN climo c on (a.sday = c.sday)
    WHERE a.station = 'IA2203' ORDER by day ASC
    """)

    running = 0
    maxrunning = 0
    for row in cursor:
        if row[1] < (row[2] - 3):
            running += 1
            if running > 10 and row[0].year > 2006:
                print("   running: %s date: %s" % (running, row[0]))
            if running > maxrunning:
                print("maxrunning: %s date: %s" % (maxrunning, row[0]))
                maxrunning = running
        else:
            running = 0


if __name__ == '__main__':
    main()
