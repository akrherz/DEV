"""We got some entered, pil, bbb combos > 2, which need some help."""

from datetime import datetime, timezone

import click
from sqlalchemy import text

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.product import TextProduct, TextProductException
from pyiem.util import logger, utc

LOG = logger()


def compute_ugcs(products: pd.DataFrame, utc_valid: datetime):
    """Figure out the UGCS for each product in the dataframe."""
    products["ugcs"] = None
    for idx, row2 in products.iterrows():
        try:
            prod = TextProduct(row2["data"], utcnow=utc_valid)
            products.at[idx, "product_id"] = prod.get_product_id()
            if prod.segments[0].ugcexpire is None:
                LOG.info(
                    "%s %s has no ugcexpire",
                    prod.get_product_id(),
                    row2["ctid"],
                )
                continue
        except TextProductException as exp:
            print("Swallowing", exp)
            continue
        except Exception as exp:
            print(exp)
            continue
        products.at[idx, "ugcs"] = ",".join(
            str(x) for x in prod.segments[0].ugcs
        ) + prod.segments[0].ugcexpire.strftime("%Y%m%d%H%M")


def process(row):
    """Figure out what to do."""
    # Find all entries for the given entered, pil
    with get_sqlalchemy_conn("afos") as conn:
        products = pd.read_sql(
            text("""
            select ctid, bbb, data, tableoid::regclass as table from
            products where entered = :entered and
            pil = :pil
            """),
            conn,
            params={
                "entered": row["utc_valid"],
                "pil": row["pil"],
            },
        )
    compute_ugcs(products, row["utc_valid"])
    if products["ugcs"].isna().any():
        return
    # the previous logic was suboptimal and was removed


@click.command()
@click.option("--year", type=int, help="Year to process")
@click.option("--pil", help="PIL (3 char) to process")
def main(year, pil):
    """Go Main Go."""
    # build a list of problematic products
    with get_sqlalchemy_conn("afos") as conn:
        products = pd.read_sql(
            text("""
            select entered at time zone 'UTC' as utc_valid,
            pil, bbb, count(*) from products where entered >= :sts and
            entered < :ets and substr(pil, 1, 3) = :pil
            GROUP by utc_valid, pil, bbb HAVING count(*) > 1
            """),
            conn,
            params={
                "sts": utc(year, 1, 1),
                "ets": utc(year + 1, 1, 1),
                "pil": pil,
            },
        )
        if products.empty:
            LOG.info("No results found!")
            return
        products["utc_valid"] = products["utc_valid"].dt.tz_localize(
            timezone.utc
        )
        LOG.info("Found %s rows to process", len(products.index))
        for _, row in products.iterrows():
            process(row)


if __name__ == "__main__":
    main()
