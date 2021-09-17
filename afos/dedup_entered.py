"""Deduplicate products stored at different timestamps.

Over the years, we had different timestamp storing logic, so sometimes
products are duplicated by having one product with the old timestamp logic
and a new one at the new logic.
"""
import sys

import pandas as pd
from pyiem.util import noaaport_text, get_dbconn
from pyiem.nws.product import TextProduct


def do(pgconn, date):
    """Go main go"""
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    # Get all the products for the date!
    ts1 = date.strftime("%Y-%m-%d 00:00+00")
    ts2 = date.strftime("%Y-%m-%d 23:59+00")
    table = "products_%s_%s" % (
        date.year,
        "0106" if date.month < 7 else "0712",
    )
    cursor.execute(
        f"SELECT ctid, entered, data from {table} where "
        "entered >= %s and entered <= %s ORDER by entered ASC",
        (ts1, ts2),
    )
    for row in cursor:
        try:
            prod = TextProduct(row[2], utcnow=row[1], parse_segments=False)
        except Exception:
            continue
        if prod.valid == row[1]:
            continue
        table2 = "products_%s_%s" % (
            prod.valid.year,
            "0106" if prod.valid.month < 7 else "0712",
        )
        # can't cross partitions with this logic here
        if table != table2:
            continue
        delta = (prod.valid - row[1]).total_seconds()
        # 30 minute tolerance
        if abs(delta) > 1800:
            continue
        cursor2.execute(
            f"UPDATE {table} SET entered = %s, data = %s WHERE ctid = %s",
            (prod.valid, noaaport_text(row[2]), row[0]),
        )
        print(f"{row[1]} -> {prod.valid} ({delta})")
    cursor2.close()
    pgconn.commit()


def main(argv):
    """Do Main"""
    pgconn = get_dbconn("afos")
    year = int(argv[1])
    for date in pd.date_range(f"{year}/01/01", f"{year}/12/31"):
        do(pgconn, date)


if __name__ == "__main__":
    main(sys.argv)
