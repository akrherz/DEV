"""Address problems found with akrherz/pyIEM/issues/1104 improvements."""

import re
import sys
from datetime import timezone
from unittest.mock import Mock

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn, sql_helper
from pyiem.nws.products.taf import ddhhmi2valid
from tqdm import tqdm

DDRE = re.compile(r"^(\d{4})/(\d{4})\s")


def process(progress, cursor, tafid, product_id):
    """Fix by rewritting."""
    # Check 1, can we get the text
    resp = httpx.get(
        f"http://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
    )
    if resp.status_code != 200:
        progress.write(f"Failed to fetch {product_id}")
        return
    is_amendment = "TAF AMD" in resp.text
    cursor.execute(
        "update taf SET is_amendment = %s where id = %s",
        (is_amendment, tafid),
    )


@click.command()
@click.option("--year", type=int, required=True, help="Year to process")
def main(year: int):
    """Process a year."""
    with get_sqlalchemy_conn("asos") as conn:
        tafs = pd.read_sql(
            sql_helper(
                f"""
    SELECT taf_id, f.valid at time zone 'UTC' as utc_valid, raw
    from taf{year} f JOIN taf t on (f.taf_id = t.id)
    where ftype = 0 and issue is null limit 10000""",
            ),
            conn,
            parse_dates=["utc_valid"],
        )
    tafs["utc_valid"] = tafs["utc_valid"].dt.tz_localize(timezone.utc)
    progress = tqdm(total=len(tafs.index))
    conn, cursor = get_dbconnc("asos")
    updates = 0
    for _, row in tafs.iterrows():
        raw = row["raw"].strip()
        m = DDRE.match(raw)
        if m is None:
            progress.write(f"{row['taf_id']} -> `{row['raw']}`")
            continue
        raw = raw.split(" ", maxsplit=1)[1]
        prod = Mock()
        prod.valid = row["utc_valid"]
        d = m.groups()
        issue = ddhhmi2valid(prod, f"{d[0]}00", row["utc_valid"])
        expire = ddhhmi2valid(prod, f"{d[1]}00", row["utc_valid"])
        cursor.execute(
            "update taf set issue = %s, expire = %s where id = %s",
            (issue, expire, row["taf_id"]),
        )
        res = cursor.execute(
            f"update taf{year} set raw = %s where taf_id = %s and ftype = 0",
            (raw, row["taf_id"]),
        )
        if res.rowcount != 1:
            print(row)
            sys.exit()
        updates += 1
        if updates % 1_000 == 0:
            cursor.close()
            conn.commit()
            cursor = conn.cursor()
        progress.update(1)
    conn.commit()


if __name__ == "__main__":
    main()
