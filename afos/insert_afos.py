"""We have duplicated old data, one with a AFOS/AWIPS ID and one without."""

from datetime import timezone

import click
from sqlalchemy import text

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import logger, utc

LOG = logger()


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
        for idx, row in products.iterrows():
            bbbcomp = "bbb = :bbb" if row["bbb"] is not None else "bbb is null"
            res = conn.execute(
                text(f"""
                select ctid, tableoid::regclass as tablename, data from
                products where entered = :entered and pil = :pil and
                {bbbcomp}
                """),
                {
                    "entered": row["utc_valid"],
                    "pil": row["pil"],
                    "bbb": row["bbb"],
                },
            )
            for prodrow in res.fetchall():
                prodlines = prodrow[2].split("\n")
                if prodlines[2].startswith(pil):
                    continue
                prodlines.insert(2, row["pil"])
                newdata = "\n".join(prodlines)
                LOG.info(
                    "Updating %s %s %s",
                    row["utc_valid"],
                    row["pil"],
                    repr(newdata[:50]),
                )
                conn.execute(
                    text(f"""
                    UPDATE {prodrow[1]} SET data = :data
                    WHERE ctid = :ctid
                    """),
                    {"data": newdata, "ctid": prodrow[0]},
                )
                conn.commit()


if __name__ == "__main__":
    main()
