"""Deduplicate products stored at different timestamps.

Over the years, we had different timestamp storing logic, so sometimes
products are duplicated by having one product with the old timestamp logic
and a new one at the new logic.
"""

import click

import pandas as pd
from pyiem.database import get_dbconn
from pyiem.nws.product import TextProduct
from pyiem.util import noaaport_text


def do(pgconn, dt):
    """Go main go"""
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    # Get all the products for the date!
    ts1 = dt.strftime("%Y-%m-%d 00:00+00")
    ts2 = dt.strftime("%Y-%m-%d 23:59+00")
    table = "products_%s_%s" % (
        dt.year,
        "0106" if dt.month < 7 else "0712",
    )
    cursor.execute(
        f"SELECT ctid, entered, data, pil from {table} where "
        "entered >= %s and entered <= %s and substr(pil, 1, 3) = 'LSR' "
        "ORDER by entered ASC",
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
        print(f"{row[3]} {row[1]} -> {prod.valid} ({delta})")
    cursor2.close()
    pgconn.commit()


@click.command()
@click.option("--year", type=int, required=True)
def main(year: int):
    """Do Main"""
    pgconn = get_dbconn("afos")
    for dt in pd.date_range(f"{year}/01/01", f"{year}/12/31"):
        do(pgconn, dt)


if __name__ == "__main__":
    main()
