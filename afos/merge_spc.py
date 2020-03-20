"""Merge some dumps from SPC."""
import os

from pyiem.util import get_dbconn, utc, noaaport_text


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    os.chdir("/tmp/NAWIPSOPS/archive/OUTLOOK/2002/pts/")
    for fn in os.listdir("."):
        ts = utc(
            int(fn[11:15]),
            int(fn[15:17]),
            int(fn[17:19]),
            int(fn[19:21]),
            int(fn[21:23]),
        )
        cursor.execute(
            """
            DELETE from products where pil = 'PTSDY1' and
            entered = %s
        """,
            (ts,),
        )
        if cursor.rowcount == 0:
            print("%s is new" % (ts,))
        data = (
            ts.strftime("000 \r\r\nWUUS01 KWNS %d%H%M\r\r\nPTSDY1\r\r\n\r\r\n")
            + open(fn).read()
        )
        txt = noaaport_text(data)
        table = "products_%s_%s" % (
            ts.year,
            "0106" if ts.month < 7 else "0712",
        )
        cursor.execute(
            """
            INSERT into """
            + table
            + """(data, pil, entered, source, wmo)
            VALUES (%s, 'PTSDY1', %s, 'KWNS', 'WUUS01')
        """,
            (txt, ts),
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
