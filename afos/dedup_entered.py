"""Deduplicate products stored at different timestamps.

Over the years, we had different timestamp storing logic, so sometimes
products are duplicated by having one product with the old timestamp logic
and a new one at the new logic.
"""

from datetime import datetime

import click
import pandas as pd
from pyiem.database import get_dbconn
from pyiem.nws.product import TextProduct


def do(pgconn, dt: datetime):
    """Go main go"""
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    # Get all the products for the date!
    ts1 = dt.strftime("%Y-%m-%d 00:00+00")
    ts2 = dt.strftime("%Y-%m-%d 23:59+00")
    table = f"products_{dt:%Y}_{'0106' if dt.month < 7 else '0712'}"
    cursor.execute(
        f"SELECT ctid, entered, data, pil, bbb from {table} where "
        "entered >= %s and entered <= %s "
        "ORDER by entered ASC",
        (ts1, ts2),
    )
    for row in cursor:
        try:
            prod = TextProduct(
                row[2], utcnow=row[1], parse_segments=False, ugc_provider={}
            )
        except Exception:
            continue
        if prod.valid == row[1] and prod.bbb == row[4]:
            continue
        table2 = (
            f"products_{prod.valid:%Y}_"
            f"{'0106' if prod.valid.month < 7 else '0712'}"
        )
        # can't cross partitions with this logic here
        if table != table2:
            continue
        delta = (prod.valid - row[1]).total_seconds()
        # 6 hour tolerance
        if abs(delta) > (6 * 3_600):
            continue
        cursor2.execute(
            f"UPDATE {table} SET entered = %s, bbb = %s WHERE ctid = %s",
            (prod.valid, prod.bbb, row[0]),
        )
        print(f"{row[3]} {row[1]} {row[4]} {prod.valid} ({delta}) {prod.bbb}")
    cursor2.close()
    pgconn.commit()


@click.command()
@click.option("--year", type=int, required=True)
def main(year: int):
    """Do Main"""
    pgconn = get_dbconn("afos")
    for dt in pd.date_range(f"{year}/05/30", f"{year}/06/30"):
        do(pgconn, dt)


if __name__ == "__main__":
    main()
