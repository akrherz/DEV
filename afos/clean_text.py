"""Some products went in the database with some cruft."""

import re
import sys

import pandas as pd
from pyiem.util import get_dbconn, noaaport_text

MYRE = re.compile("[A-Z0-9]{5,6} [A-Z]{4} [0-9]{5,6}")


def do_date(pgconn, date):
    """Process a given date."""
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute(
        "SELECT data, ctid, tableoid::regclass as tablename "
        "from products WHERE entered >= %s and "
        "entered <= %s and substr(data, 12, 1) = ':'",
        (
            date.strftime("%Y-%m-%d 00:00+00"),
            date.strftime("%Y-%m-%d 23:59+00"),
        ),
    )
    updates = 0
    for row in cursor:
        meat = row[0].split(":", 2)
        if meat[1].find("\n") > -1:
            print(meat)
            sys.exit()
        text = noaaport_text(meat[2])
        cursor2.execute(
            f"UPDATE {row[2]} SET data = %s where ctid = %s", (text, row[1])
        )
        updates += cursor2.rowcount
    print(f"{date} {updates} updates")
    cursor2.close()
    pgconn.commit()


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    pgconn = get_dbconn("afos")
    for date in pd.date_range(f"{year}/01/01", f"{year}/12/31"):
        do_date(pgconn, date)


if __name__ == "__main__":
    main(sys.argv)
