"""Process SPS again for new storage."""

from pyiem.database import get_dbconn
from pyiem.nws.products.sps import parser
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    dbconn = get_dbconn("postgis")
    cursor = dbconn.cursor()
    for text in open("SPS.txt", "rb").read().split(b"\003"):
        try:
            prod = parser(text.decode("ascii"))
            if prod.afos is None:
                print(repr(text[:100]))
                return
        except Exception as exp:
            LOG.exception(exp)
            continue
        cursor.execute(
            "SELECT product_id from sps WHERE product_id = %s",
            (prod.get_product_id(),),
        )
        if cursor.rowcount > 0:
            LOG.info(
                "skipping %s",
                prod.get_product_id(),
            )
            continue
        LOG.info("insert")
        prod.sql(cursor)
    cursor.close()
    dbconn.commit()


if __name__ == "__main__":
    main()
