"""
Script to set/backfill the product_id field in the database.
"""

from datetime import datetime, timezone

import click
import pandas as pd
from psycopg import Connection
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.nws.products.lsr import parser
from pyiem.util import logger, utc
from sqlalchemy import text

LOG = logger()


def do(dt, conn: Connection):
    """Find things to update."""
    acursor = get_dbconn("afos").cursor()
    acursor.execute(
        """
        SELECT entered at time zone 'UTC', data from products WHERE
        entered >= %s and entered <= %s and substr(pil, 1, 3) = 'LSR'
        and pil = 'LSRBOU' and data ~* 'BRECK'
        ORDER by entered ASC
        """,
        (
            utc(dt.year, dt.month, dt.day),
            utc(dt.year, dt.month, dt.day, 23, 59),
        ),
    )
    LOG.info("%s found %s afos entries", dt, acursor.rowcount)
    fixed = 0
    zero = 0
    for row in acursor:
        try:
            prod = parser(row[1], utcnow=row[0].replace(tzinfo=timezone.utc))
            print(prod.get_product_id())
        except Exception as exp:
            LOG.info(
                "Failed to parse %s %s %s",
                row[0],
                row[1],
                exp,
            )
            continue
        if not prod.lsrs:
            LOG.info("Product %s has no LSRS", prod.get_product_id())
            continue
        col = "product_id_summary" if prod.is_summary() else "product_id"
        for lsr in prod.lsrs:
            if lsr.city == "WSW Alachua":
                print(lsr)
            if lsr.remark and lsr.remark.find("&&") > -1:
                lsr.remark = None
            magf = lsr.magnitude_f
            tt = lsr.typetext.upper()
            res = conn.execute(
                text(f"""
                SELECT ctid, tableoid::regclass as tablename, {col}
                from lsrs where valid = :valid and typetext = :tt and
                wfo = :wfo and upper(city) = :city and
                geom = ST_Point(:lon, :lat, 4326)
                and remark is not distinct from :remark
                and source = :source and
                (magnitude is not distinct from :mag or
                 (magnitude = 0 and :mag is null))
                and upper(county) = :county
                and state = :state
                """),
                {
                    "valid": lsr.utcvalid,
                    "tt": tt,
                    "wfo": lsr.wfo,
                    "city": lsr.city.upper(),
                    "lon": lsr.geometry.x,
                    "lat": lsr.geometry.y,
                    "remark": lsr.remark,
                    "source": lsr.source,
                    "mag": magf,
                    "county": lsr.county.upper(),
                    "state": lsr.state,
                },
            )
            if res.rowcount == 0:
                zero += 1
                continue
            for row in res.mappings():
                conn.execute(
                    text(
                        f"UPDATE {row['tablename']} SET {col} = :pid, "
                        "qualifier = :q, magnitude = :mag, "
                        "unit = :unit where ctid = :ctid"
                    ),
                    {
                        "pid": prod.get_product_id(),
                        "ctid": row["ctid"],
                        "unit": lsr.magnitude_units,
                        "q": lsr.magnitude_qualifier,
                        "mag": magf,
                    },
                )
                LOG.debug(
                    "    Updated %s %s -> %s",
                    col,
                    row[col],
                    prod.get_product_id(),
                )
                fixed += 1
    LOG.info("Updated %s rows, %s failures", fixed, zero)


@click.command()
@click.option("--sts", type=click.DateTime(), required=True)
@click.option("--ets", type=click.DateTime(), required=True)
def main(sts: datetime, ets: datetime):
    """Go Main Go."""
    for dt in pd.date_range(sts.date(), ets.date()):
        with get_sqlalchemy_conn("postgis") as conn:
            do(dt, conn)
            conn.commit()


if __name__ == "__main__":
    main()
