"""These are classified as TOR,SVR, but should be SVS."""

import sys
from datetime import timezone

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.product import TextProduct, TextProductException
from pyiem.util import logger, utc
from sqlalchemy import text

LOG = logger()


@click.command()
@click.option("--year", type=int, help="Year to process")
def main(year):
    """Go Main Go."""
    if year >= 2001:
        LOG.warning("This script is only for pre-2000 data")
        return
    # build a list of problematic products
    with get_sqlalchemy_conn("afos") as conn:
        products = pd.read_sql(
            text("""
            select ctid, data, entered at time zone 'UTC' as utc_valid,
            tableoid::regclass as table,
            pil, bbb from products where entered >= :sts and
            entered < :ets and substr(pil, 1, 3) in ('SVR', 'TOR')
            ORDER by entered ASC
            """),
            conn,
            params={
                "sts": utc(year, 1, 1),
                "ets": utc(year + 1, 1, 1),
            },
        )
        products["utc_valid"] = products["utc_valid"].dt.tz_localize(
            timezone.utc
        )
        LOG.info("Found %s rows to process", len(products.index))
        for _, row in products.iterrows():
            prodtext = row["data"]
            try:
                prod = TextProduct(prodtext, utcnow=row["utc_valid"])
                if not prod.segments:
                    raise ValueError("No segments found")
            except TextProductException as exp:
                LOG.info("ctid: %s swallowing: %s", row["ctid"], exp)
            except Exception as exp:
                LOG.info("ctid: %s failed to parse: %s", row["ctid"], exp)
                continue
            ugcs = [str(x) for x in prod.segments[0].ugcs]
            # If any ugcs are counties, we keep it
            if not ugcs or any(ugc[2] == "C" for ugc in ugcs):
                continue
            lines = prodtext.split("\n")
            lines[2] = f"SVS{row['pil'][3:]}"
            newtext = "\n".join(lines)
            print(
                f"Will update, {ugcs} {prod.get_product_id()} "
                f"{repr(newtext[:40])}"
            )
            res = conn.execute(
                text(f"""
                update {row['table']} SET pil = :pil, bbb = :bbb, data = :data
                WHERE ctid = :ctid
            """),
                {
                    "pil": lines[2],
                    "bbb": prod.bbb,
                    "data": newtext,
                    "ctid": row["ctid"],
                },
            )
            if res.rowcount != 1:
                LOG.info("Failed to update ctid: %s", row["ctid"])
                sys.exit()
            conn.commit()


if __name__ == "__main__":
    main()
