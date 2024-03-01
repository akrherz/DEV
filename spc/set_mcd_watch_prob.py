"""Update database storage of watch_confidence."""

import sys

from pyiem.nws.products import mcd
from pyiem.util import get_dbconn, noaaport_text


def main(argv):
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute(
        "SELECT product_id, product, num from mcd where "
        "watch_confidence is null and year = %s ORDER by num ASC",
        (int(argv[1]),),
    )
    for row in cursor:
        try:
            prod = mcd.parser(noaaport_text(row[1]))
        except Exception:
            print(f"{row[2]} fail")
            continue
        val = prod.find_watch_probability()
        cursor2.execute(
            "UPDATE mcd SET watch_confidence = %s where product_id = %s",
            (val, row[0]),
        )

    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
