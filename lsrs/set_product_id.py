"""
Script to set/backfill the product_id field in the database.
"""

import datetime
from itertools import product

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
    zero = 0
    for row in acursor:
        try:
            prod = parser(
                row[1], utcnow=row[0].replace(tzinfo=datetime.timezone.utc)
            )
        except Exception:
            continue
        for lsr in prod.lsrs:
            magf = lsr.magnitude_f
            magu = lsr.magnitude_units
            tt = lsr.typetext.upper()
            op2 = "is" if lsr.remark is None else "="
            op3 = "is" if magu is None else "="
            opt2 = (
                ["SNOW", "HEAVY SNOW"]
                if tt.find("SNOW") > -1
                else [
                    tt,
                ]
            )
            opts = (
                [magf, 0]
                if magf is None
                else [
                    magf,
                ]
            )
            if tt == "T" and magf is not None and magf == 0:
                opts = [0, None]
            for _tt, _magf in product(opt2, opts):
                op = "is" if _magf is None else "="
                cursor.execute(
                    f"""
                    SELECT ctid, tableoid::regclass as tablename
                    from lsrs where valid = %s and typetext = %s and
                    wfo = %s and city = %s and geom = %s and remark {op2} %s
                    and source = %s and magnitude {op} %s and county = %s
                    and state = %s and unit {op3} %s
                    """,
                    (
                        lsr.utcvalid,
                        _tt,
                        lsr.wfo,
                        lsr.city,
                        f"SRID=4326;{lsr.geometry.wkt}",
                        lsr.remark,
                        lsr.source,
                        _magf,
                        lsr.county,
                        lsr.state,
                        lsr.magnitude_units,
                    ),
                )
                if cursor.rowcount == 1:
                    break
            if cursor.rowcount == 0:
                zero += 1
            if cursor.rowcount == 1:
                row = cursor.fetchone()
                cursor.execute(
                    f"UPDATE {row[1]} SET product_id = %s, typetext = %s, "
                    "magnitude = %s where ctid = %s",
                    (prod.get_product_id(), tt, magf, row[0]),
                )
                fixed += 1
    LOG.info("Fixed %s rows, %s failures", fixed, zero)


def main():
    """Go Main Go."""
    conn = get_dbconn("postgis")
    for dt in pd.date_range("2007/01/01", "2008/12/31"):
        cursor = conn.cursor()
        do(dt, cursor)
        cursor.close()
        conn.commit()


if __name__ == "__main__":
    main()
