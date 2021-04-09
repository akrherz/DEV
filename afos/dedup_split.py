"""Deduplicate."""
import sys
import re
from datetime import datetime
import difflib

from tqdm import tqdm
from pyiem.util import noaaport_text, get_dbconn
import pandas as pd
from pandas.io.sql import read_sql

DATE_RE = re.compile("\d+/\d+/\d+")


def dotable(date):
    """Go main go"""
    ts1 = date.strftime("%Y-%m-%d 00:00+00")
    ts2 = date.strftime("%Y-%m-%d 23:59+00")
    table = "products_%s_%s" % (
        date.year,
        "0106" if date.month < 7 else "0712",
    )
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute(
        f"""
        SELECT ctid, entered, data from {table}
        WHERE pil in ('SWODY1', 'SWODY2')
        and entered >= %s and entered <= %s and data ~* '/0'
        ORDER by entered
        """,
        (ts1, ts2),
    )
    for row in cursor:
        try:
            ts = datetime.strptime(DATE_RE.findall(row[2])[0], "%m/%d/%y")
        except (ValueError, IndexError):
            print(row[2])
            continue
        if ts.year != 2001:
            print(f"Deleting {ts} {row[1]}")
            cursor2.execute(
                f"DELETE from {table} WHERE ctid = %s",
                (row[0],),
            )

    cursor2.close()
    pgconn.commit()
    pgconn.close()


def main(argv):
    """Do Main"""
    year = int(argv[1])
    for date in pd.date_range(f"{year}/01/02", f"{year}/12/30"):
        dotable(date)


if __name__ == "__main__":
    main(sys.argv)
