"""Update database storage of mpd/mcd concerning."""

import sys

from pyiem.nws.products import mcd
from pyiem.util import get_dbconn, noaaport_text


def main(argv):
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute(
        f"SELECT product_id, product, num, year, concerning from {argv[1]} "
        "where product is not null and concerning is not null "
        "ORDER by year ASC, num ASC",
    )
    for row in cursor:
        try:
            prod = mcd.parser(noaaport_text(row[1]))
        except Exception as exp:
            print(f"{row[2]} {row[3]} fail {exp}")
            continue
        val = prod.concerning
        if val == row[4]:
            continue
        print(f"|{row[4]}| -> |{val}|")
        cursor2.execute(
            f"UPDATE {argv[1]} SET concerning = %s where product_id = %s "
            "and num = %s and year = %s",
            (val, row[0], row[2], row[3]),
        )
        assert cursor2.rowcount == 1

    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
