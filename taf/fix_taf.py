"""Address problems found with akrherz/pyIEM/issues/1104 improvements."""

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn, sql_helper
from pyiem.util import utc
from tqdm import tqdm


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
                """
    SELECT id, product_id FROM taf where valid >= :sts and valid < :ets
    and is_amendment is null limit 10000""",
                table=f"taf{year}",
            ),
            conn,
            params={"sts": utc(year), "ets": utc(year + 1)},
        )
    progress = tqdm(total=len(tafs.index))
    conn, cursor = get_dbconnc("asos")
    updates = 0
    for _, row in tafs.iterrows():
        progress.set_description(f"{row['product_id']:38s}")
        process(progress, cursor, row["id"], row["product_id"])
        updates += 1
        if updates % 1_000 == 0:
            cursor.close()
            conn.commit()
            cursor = conn.cursor()
        progress.update(1)
    conn.commit()


if __name__ == "__main__":
    main()
