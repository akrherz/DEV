"""
Reprocess Summary LSRs to update database schema.

refs akrherz/pyWWA#150
"""

from pyiem.nws.products.lsr import parser
from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main Go."""
    dbconn = get_dbconn("postgis")
    cursor = dbconn.cursor()
    updated = 0
    for text in open("LSR.txt", "rb").read().split(b"\003"):
        try:
            prod = parser(text.decode("ascii", errors="ignore"))
            if prod.afos is None:
                print(repr(text[:100]))
                continue
        except Exception as exp:
            LOG.exception(exp)
            continue
        updated += len(prod.lsrs)
        LOG.info("Product: %s lsrs: %s", prod.get_product_id(), len(prod.lsrs))
        for lsr in prod.lsrs:
            lsr.duplicate = True
            lsr.sql(cursor)
        if updated > 500:
            cursor.close()
            dbconn.commit()
            cursor = dbconn.cursor()
            updated = 0

    cursor.close()
    dbconn.commit()


if __name__ == "__main__":
    main()
