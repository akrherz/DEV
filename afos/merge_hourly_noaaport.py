"""Merge in hourly noaaport files found here:

http://idd.ssec.wisc.edu/native/nwstg/text/
"""

from pyiem.database import get_dbconn
from pyiem.nws.product import TextProduct
from pyiem.util import utc


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    utcnow = utc(2024, 7, 30, 4)
    with open("/mesonet/tmp/2024073003.txt", "rb") as fh:
        data = fh.read()
    for token in data.decode("ascii", "ignore").split("\003"):
        try:
            tp = TextProduct(token, utcnow=utcnow, parse_segments=False)
        except Exception as exp:
            print(exp)
            continue
        if tp.afos is None:
            continue
        cursor.execute(
            "SELECT data from products_2024_0712 where entered = %s and "
            "source = %s and wmo = %s and pil = %s",
            (tp.valid, tp.source, tp.wmo, tp.afos),
        )
        if cursor.rowcount > 0:
            continue
        print(tp.get_product_id())
        cursor.execute(
            """
        INSERT into products_2024_0712 (entered, source, wmo, pil, data, bbb)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (tp.valid, tp.source, tp.wmo, tp.afos, token, tp.bbb),
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
