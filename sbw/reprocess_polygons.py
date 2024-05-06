"""Update product_signature field for sbw."""

import click
import httpx
from sqlalchemy import text
from tqdm import tqdm

import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.nws.product import TextProduct
from pyiem.util import logger

LOG = logger()


@click.command()
@click.option("--year", type=int, help="Year to process")
def main(year):
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as pgconn:
        df = pd.read_sql(
            text(
                """
            select ctid, product_id, updated, st_area(geom) from sbw
            WHERE vtec_year = :year and
            product_id is not null and st_area(geom) < 0.001
            ORDER by polygon_begin ASC
        """
            ),
            pgconn,
            params={"year": year},
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
        except Exception as exp:
            LOG.info("Failed to parse %s %s", row["product_id"], exp)
            continue
        if prod.segments[0].sbw is None:
            LOG.info("ctid: %s has no sbw? %s", row["ctid"], row["product_id"])
            continue
        if prod.segments[0].sbw.area > row["st_area"]:
            LOG.info(
                "ctid: %s area: %.4f > %.4f",
                row["ctid"],
                prod.segments[0].sbw.area,
                row["st_area"],
            )
            cursor.execute(
                f"update sbw_{year} SET geom = %s WHERE ctid = %s",
                (prod.segments[0].giswkt, row["ctid"]),
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
