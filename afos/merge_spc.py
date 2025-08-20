"""Merge some dumps from SPC."""

import os

from pyiem.database import get_dbconn
from pyiem.util import noaaport_text, utc


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
            "DELETE from products where pil = 'PTSDY1' and entered = %s",
            (ts,),
        )
        if cursor.rowcount == 0:
            print("%s is new" % (ts,))
        data = (
            ts.strftime("000 \nWUUS01 KWNS %d%H%M\nPTSDY1\n\n")
            + open(fn).read()
        )
        txt = noaaport_text(data)
        table = f"products_{ts.year}_{'0106' if ts.month < 7 else '0712'}"
        cursor.execute(
            f"INSERT into {table} (data, pil, entered, source, wmo) "
            "VALUES (%s, 'PTSDY1', %s, 'KWNS', 'WUUS01')",
            (txt, ts),
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
