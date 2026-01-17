"""At some point, I failed to backfill the qualifier."""

from datetime import datetime

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.nws.products.lsr import parser
from pyiem.util import logger, utc

LOG = logger()


def do(dt: datetime, cursor):
    """Find things to update."""
    table = f"lsrs_{dt:%Y}"
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            sql_helper(
                f"""
            select ctid, *, st_x(geom) as lon, st_y(geom) as lat
            from {table} WHERE valid >= :sts and valid <= :ets
            and (qualifier is null or qualifier = '')
            and product_id is not null and magnitude is not null
            """
            ),
            {
                "sts": utc(dt.year, dt.month, dt.day),
                "ets": utc(dt.year, dt.month, dt.day, 23, 59),
            },
        )
        LOG.info("Found %s rows to update", res.rowcount)
        fixed = 0
        zero = 0
        for row in res.mappings():
            resp = httpx.get(
                "https://mesonet.agron.iastate.edu/api/1/"
                f"nwstext/{row['product_id']}?nolimit=1"
            )
            if resp.status_code != 200:
                LOG.info("Failed to fetch %s", row["product_id"])
                continue
            found = False
            for content in resp.text.split("\003"):
                if content.strip() == "":
                    continue
                try:
                    prod = parser(content)
                except Exception as exp:
                    LOG.info("Failed to parse %s: %s", row["product_id"], exp)
                    print(repr(content[:100]))
                    continue
                for lsr in prod.lsrs:
                    if (
                        lsr.magnitude_qualifier is None
                        or lsr.magnitude_f is None
                        or found
                    ):
                        continue
                    if (
                        lsr.valid == row["valid"]
                        and lsr.wfo == row["wfo"]
                        and abs(lsr.magnitude_f - float(row["magnitude"]))
                        < 0.1
                        and lsr.typetext == row["typetext"]
                        and lsr.city == row["city"]
                        and lsr.county == row["county"]
                        and lsr.state == row["state"]
                        and lsr.source == row["source"]
                        and abs(lsr.get_lat() - row["lat"]) < 0.01
                        and abs(lsr.get_lon() - row["lon"]) < 0.01
                    ):
                        cursor.execute(
                            f"UPDATE {table} SET qualifier = %s "
                            "WHERE ctid = %s",
                            (lsr.magnitude_qualifier, row["ctid"]),
                        )
                        fixed += 1
                        found = True
            if not found:
                # if row["type"] == "S":
                #    print(lsr)
                #    print(row)
                #    sys.exit()
                zero += 1
    LOG.info("Fixed %s rows for %s, %s failures", fixed, dt, zero)


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
