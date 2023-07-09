"""
Script to set/backfill the product_id field in the database.
"""
import datetime

import pandas as pd
from pyiem.nws.products.lsr import parser
from pyiem.util import get_dbconn, logger, utc

LOG = logger()


def do(dt, cursor):
    """Find things to update."""
    acursor = get_dbconn("afos").cursor()
    acursor.execute(
        """
        SELECT entered at time zone 'UTC', data from products WHERE
        entered >= %s and entered <= %s and substr(pil, 1, 3) = 'LSR'
        ORDER by entered ASC
        """,
        (
            utc(dt.year, dt.month, dt.day),
            utc(dt.year, dt.month, dt.day, 23, 59),
        ),
    )
    LOG.info("%s found %s afos entries", dt, acursor.rowcount)
    fixed = 0
    for row in acursor:
        try:
            prod = parser(
                row[1], utcnow=row[0].replace(tzinfo=datetime.timezone.utc)
            )
        except Exception:
            continue
        for lsr in prod.lsrs:
            cursor.execute(
                """
                SELECT ctid, tableoid::regclass as tablename
                from lsrs where valid = %s and typetext = %s and
                wfo = %s and city = %s and geom = %s and remark = %s
                """,
                (
                    lsr.utcvalid,
                    lsr.typetext.upper(),
                    lsr.wfo,
                    lsr.city,
                    f"SRID=4326;{lsr.geometry.wkt}",
                    lsr.remark,
                ),
            )
            # if cursor.rowcount > 1:
            #    print(lsr)
            if cursor.rowcount == 1:
                row = cursor.fetchone()
                cursor.execute(
                    f"UPDATE {row[1]} SET product_id = %s where ctid = %s",
                    (prod.get_product_id(), row[0]),
                )
                fixed += 1
    LOG.info("Fixed %s rows", fixed)


def main():
    """Go Main Go."""
    conn = get_dbconn("postgis")
    for dt in pd.date_range("2013/12/07", "2020/01/01"):
        cursor = conn.cursor()
        do(dt, cursor)
        cursor.close()
        conn.commit()


if __name__ == "__main__":
    main()
