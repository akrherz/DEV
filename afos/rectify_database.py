"""Ensure that database entries have things set correctly.

aka, atone for the sins of the past.
"""

import sys
from datetime import datetime

import click
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.util import utc
from pyiem.wmo import WMOProduct
from pywwa.workflows.fake_afos_dump import compute_afos
from sqlalchemy.engine import Connection
from tqdm import tqdm


def is_duplicate(prod: WMOProduct, row: dict) -> bool:
    """Check if this is a duplicate"""
    # Text should match
    if prod.unixtext != row["data"]:
        print("Text %s != %s" % (len(prod.unixtext), len(row["data"])))
        return False
    # Check that bbb matches - either both None or equal values
    if prod.bbb != row["bbb"]:
        print("BBB %s != %s" % (prod.bbb, row["bbb"]))
        return False
    # Check that timestamps are equal
    if prod.valid != row["entered"]:
        print("Valid %s != %s" % (prod.valid, row["entered"]))
        return False
    # Check that pil and afos match
    if prod.afos != row["pil"]:
        print(f"AFOS {prod.afos} != {row['pil']}")
        return False
    return True


@with_sqlalchemy_conn("afos")
def do(progress, dt: datetime, limiters: dict, conn: Connection = None):
    """Go main go"""
    # Get all the products for the date!
    ts1 = utc(dt.year, dt.month, dt.day)
    ts2 = ts1.replace(hour=23, minute=59)
    table = f"products_{dt:%Y}_{'0106' if dt.month < 7 else '0712'}"
    limitsql = ""
    for key in ["source", "pil"]:
        if limiters[key] is not None:
            limitsql += f" and {key} = :{key}"
    # DSM is a one-off product without WMO header
    res = conn.execute(
        sql_helper(
            """
    SELECT ctid, entered, data, trim(pil) as pil, bbb from {table} where
    entered >= :sts and entered <= :ets {limitsql}
    and substr(pil, 1, 3) != 'DSM' ORDER by entered ASC""",
            table=table,
            limitsql=limitsql,
        ),
        {"sts": ts1, "ets": ts2, **limiters},
    )
    dups = 0
    updates = 0
    aborts = 0
    leave_stamp = 0
    for row in res.mappings():
        try:
            prod = WMOProduct(row["data"], utcnow=row["entered"])
        except Exception:
            aborts += 1
            continue
        try:
            if prod.afos is None:
                compute_afos(prod)
        except Exception:
            pass
        # Allows for None check for bbb
        if is_duplicate(prod, row):
            dups += 1
            continue
        table2 = (
            f"products_{prod.valid:%Y}_"
            f"{'0106' if prod.valid.month < 7 else '0712'}"
        )
        # can't cross partitions with this logic here
        if table != table2:
            aborts += 1
            continue
        delta = (prod.valid - row["entered"]).total_seconds()
        # 6 hour tolerance
        if abs(delta) > (6 * 3_600):
            leave_stamp += 1
            prod.valid = row["entered"]
        conn.execute(
            sql_helper(
                """
    UPDATE {table} SET entered = :valid, bbb = :bbb, pil = :pil, data = :data
    WHERE ctid = :ctid
            """,
                table=table,
            ),
            {
                "valid": prod.valid,
                "bbb": prod.bbb,
                "ctid": row["ctid"],
                "pil": prod.afos,
                "data": prod.unixtext,
            },
        )
        updates += 1
    progress.write(
        f"{ts1:%Y%m%d} Found {dups} duplicates, "
        f"{updates} updates, {aborts} aborts, and {leave_stamp} leave_stamps"
    )
    conn.commit()


@click.command()
@click.option("--sdate", type=click.DateTime(), required=True)
@click.option("--edate", type=click.DateTime(), required=True)
@click.option("--source", type=str, help="Limit to this source")
@click.option("--pil", type=str, help="Limit to this pil")
def main(
    sdate: datetime, edate: datetime, source: str | None, pil: str | None
):
    """Do Main"""
    sts = sdate.date()
    ets = edate.date()
    limiters = {
        "source": source,
        "pil": pil,
    }
    progress = tqdm(pd.date_range(sts, ets, freq="1D"), file=sys.stderr)
    for dt in progress:
        progress.set_description(f"Processing {dt:%Y-%m-%d}")
        do(progress, dt, limiters)


if __name__ == "__main__":
    main()
