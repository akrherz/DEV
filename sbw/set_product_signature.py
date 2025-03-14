"""Update product_signature field for sbw."""

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.nws.product import TextProduct
from pyiem.util import logger
from sqlalchemy import text
from tqdm import tqdm

LOG = logger()


@click.command()
@click.option("--year", type=int, help="Year to process")
def main(year):
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as pgconn:
        df = pd.read_sql(
            text(
                f"""
            select ctid, product_id, updated from sbw_{year} WHERE
            product_id is not null and product_signature is null
        """
            ),
            pgconn,
        )
    LOG.info("Found %s rows to process", len(df.index))
    pgconn, cursor = get_dbconnc("postgis")

    updates = 0
    for _, row in tqdm(df.iterrows(), total=len(df.index)):
        req = httpx.get(
            "https://mesonet.agron.iastate.edu/api/1/nwstext"
            f"/{row['product_id']}"
        )
        try:
            prod = TextProduct(req.text, utcnow=row["updated"])
            sig = prod.get_signature()
        except Exception as exp:
            LOG.info("Failed to parse %s %s", row["product_id"], exp)
            continue
        if sig is None:
            continue
        cursor.execute(
            f"update sbw_{year} SET product_signature = %s WHERE ctid = %s",
            (sig, row["ctid"]),
        )
        updates += 1
        if updates % 100 == 0:
            cursor.close()
            pgconn.commit()
            cursor = pgconn.cursor()
    LOG.info("Updated %s rows", updates)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
