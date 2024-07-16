"""
Requested cross check.
"""

import click
import httpx
from sqlalchemy import text

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.products.vtec import VTECProduct


@click.command()
@click.option("--year", type=int, help="Year to work on...")
def main(year):
    """Go Main Go."""
    # Find a batch of product_ids that need to be run
    with get_sqlalchemy_conn("postgis") as conn:
        warnings = pd.read_sql(
            text("""
            select product_id from sbw WHERE vtec_year = :year and
            status = 'NEW'  and phenomena = 'MA'
            and wfo = 'CHS'
            order by product_id
            """),
            conn,
            params=dict(
                year=year,
            ),
        )
    for _, row in warnings.iterrows():
        prodtext = httpx.get(
            "http://mesonet.agron.iastate.edu/api/1/nwstext"
            f"/{row['product_id']}"
        ).text
        # if prodtext.find("Until ") == -1:
        #    continue
        prod = VTECProduct(prodtext)
        vtecexpire = prod.segments[0].vtec[0].endts
        if vtecexpire is None:
            continue
        stamp = vtecexpire.astimezone(prod.tz)
        lookfor = (
            stamp.strftime("Until %-I%M %p %Z")
            .replace("1200 PM", "noon")
            .replace("1200 AM", "midnight")
        )
        pos = prodtext.find(lookfor)
        if pos == -1:
            print(prod.get_product_id(), stamp, lookfor)
            continue


if __name__ == "__main__":
    main()
