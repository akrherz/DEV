"""Disconnect between product_id storage in LSR and what afos has..."""

from datetime import datetime, timedelta, timezone

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import logger, utc
from sqlalchemy import text

LOG = logger()


def do(dt: datetime, cursor):
    """Find things to update."""
    table = f"lsrs_{dt:%Y}"
    with (
        get_sqlalchemy_conn("postgis") as conn,
        get_sqlalchemy_conn("afos") as aconn,
    ):
        res = conn.execute(
            text(
                f"""
            select distinct product_id
            from {table} WHERE valid >= :sts and valid <= :ets
            and product_id is not null
            """
            ),
            {
                "sts": utc(dt.year, dt.month, dt.day),
                "ets": utc(dt.year, dt.month, dt.day, 23, 59),
            },
        )
        LOG.info("Found %s rows for %s to check", res.rowcount, dt)
        for row in res.mappings().fetchall():
            resp = httpx.get(
                "https://mesonet.agron.iastate.edu/api/1/"
                f"nwstext/{row['product_id']}"
            )
            if resp.status_code == 200:
                continue
            # 201901191638-KILX-NWUS53-LSRILX
            tokens = row["product_id"].split("-")
            pil = tokens[3]
            bbb = None
            if len(tokens) == 5:
                bbb = tokens[4]
            entered = datetime.strptime(row["product_id"][:12], "%Y%m%d%H%M")
            entered = entered.replace(tzinfo=timezone.utc)
            ares = aconn.execute(
                text(
                    """select entered at time zone 'UTC' as utc_entered,
                source, wmo, pil, bbb from products
                where pil = :pil and
                entered >= :sts and entered <= :ets
                and bbb is not distinct from :bbb
                ORDER by entered DESC"""
                ),
                {
                    "sts": entered - timedelta(minutes=1),
                    "ets": entered + timedelta(minutes=0),
                    "pil": pil,
                    "bbb": bbb,
                },
            )
            if ares.rowcount == 1:
                arow = ares.first()
                new_product_id = (
                    f"{arow[0]:%Y%m%d%H%M}-{arow[1]}-{arow[2]}-{arow[3]}"
                )
                if arow[4] is not None:
                    new_product_id += f"-{arow[4]}"
                res = conn.execute(
                    text(
                        f"update {table} "
                        "SET product_id = :new where product_id = :old"
                    ),
                    {"new": new_product_id, "old": row["product_id"]},
                )
                LOG.info(
                    "Updated %s rows for %s -> %s",
                    res.rowcount,
                    row["product_id"],
                    new_product_id,
                )

                conn.commit()
            else:
                LOG.info(
                    "No match for %s %s %s",
                    row["product_id"],
                    pil,
                    entered,
                )


@click.command()
@click.option("--year", type=int, required=True)
def main(year: int):
    """Go Main Go."""
    conn = get_dbconn("postgis")
    for dt in pd.date_range(f"{year}/01/01", f"{year}/12/31"):
        cursor = conn.cursor()
        do(dt, cursor)
        cursor.close()
        conn.commit()


if __name__ == "__main__":
    main()
