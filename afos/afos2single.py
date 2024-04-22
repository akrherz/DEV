"""Dump products to file."""

from pyiem.database import get_dbconnc
from pyiem.util import noaaport_text


def main():
    """Go Main Go."""
    pgconn, cursor = get_dbconnc("afos")

    cursor.execute(
        """
        select entered at time zone 'UTC' as ts, data, pil from products
        where substr(pil, 1, 3) = 'SPS' and
        source in ('KDMX', 'KDVN', 'KARX', 'KFSD', 'KOAX') and
        data ~* 'landspout' and data ~* 'IA' ORDER by entered asc
    """
    )
    for row in cursor:
        pil = row["pil"].strip()
        fn = row["ts"].strftime(f"{pil}_%Y%m%d%H%M.txt")
        with open(fn, "a", encoding="utf8") as fh:
            fh.write(noaaport_text(row["data"]))
    pgconn.close()


if __name__ == "__main__":
    main()
