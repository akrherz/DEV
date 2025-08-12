"""Address problems found with akrherz/pyIEM/issues/1104 improvements."""

from datetime import datetime, timezone

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn, sql_helper
from pyiem.nws.products.taf import parser
from tqdm import tqdm


def process(progress, cursor, year, tafid, product_id):
    """Fix by rewritting."""
    # Check 1, can we get the text
    resp = httpx.get(
        f"http://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
    )
    if resp.status_code != 200:
        progress.write(f"Failed to fetch {product_id}")
        return
    utcnow = datetime.strptime(product_id[:12], "%Y%m%d%H%M").replace(
        tzinfo=timezone.utc
    )
    # Check 2, can we parse the product
    prod = parser(resp.text, utcnow)
    if not prod.data.forecasts:
        progress.write(f"{product_id} had no forecasts")
        return
    # Step 1, delete old entry
    cursor.execute("delete from taf_forecast where taf_id = %s", (tafid,))
    cursor.execute("delete from taf where id = %s", (tafid,))
    # Step 2, insert new entry
    prod.sql(cursor)


@click.command()
@click.option("--year", type=int, required=True, help="Year to process")
def main(year: int):
    """Process a year."""
    with get_sqlalchemy_conn("asos") as conn:
        tafs = pd.read_sql(
            sql_helper(
                """
    SELECT distinct t.id, t.product_id FROM taf t JOIN {table} d
    on t.id = d.taf_id where strpos(raw, 'PROB30') > 2
    and product_id is not null """,
                table=f"taf{year}",
            ),
            conn,
        )
    progress = tqdm(total=len(tafs.index))
    conn, cursor = get_dbconnc("asos")
    for _, row in tafs.iterrows():
        progress.set_description(row["product_id"])
        process(progress, cursor, year, row["id"], row["product_id"])
        cursor.close()
        conn.commit()
        cursor = conn.cursor()
        progress.update(1)


if __name__ == "__main__":
    main()
