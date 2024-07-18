"""General consec analysis."""

import datetime
import sys

from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    site = sys.argv[1]
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    cursor.execute(
        """
    select day, max_dwpf from summary where iemid = %s and max_dwpf >= 70
    ORDER by day ASC
    """,
        (int(site),),
    )
    lastval = datetime.date(2000, 1, 1)
    running = []
    for row in cursor:
        if (lastval - row[0]) == datetime.timedelta(days=-1):
            running.append(row[0])
            lastval = row[0]
            continue
        if len(running) > 10:
            print(f"{len(running)} {running}")
        lastval = row[0]
        running = []


if __name__ == "__main__":
    main()
