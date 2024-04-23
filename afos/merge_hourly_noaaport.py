"""Merge in hourly noaaport files found here:

http://idd.ssec.wisc.edu/native/nwstg/text/
"""

from pyiem.database import get_dbconn
from pyiem.nws.products import TextProduct
from pyiem.util import utc


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    utcnow = utc(2019, 7, 20, 18)
    data = open("SURFACE_DDPLUS_20190720_1800.txt", "rb").read()
    for token in data.decode("ascii", "ignore").split("\003"):
        try:
            tp = TextProduct(token, utcnow=utcnow, parse_segments=False)
        except Exception as exp:
            print(exp)
            continue
        if tp.afos is None:
            continue
        cursor.execute(
            "SELECT data from products_2019_0712 where entered = %s and "
            "source = %s and wmo = %s and pil = %s",
            (tp.valid, tp.source, tp.wmo, tp.afos),
        )
        if cursor.rowcount > 0:
            continue
        print(tp.get_product_id())
        cursor.execute(
            """
        INSERT into products_2019_0712 (entered, source, wmo, pil, data)
        VALUES (%s, %s, %s, %s, %s)
        """,
            (tp.valid, tp.source, tp.wmo, tp.afos, token),
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
