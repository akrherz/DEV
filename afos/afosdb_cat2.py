"""Dump products to file."""
import sys

from pyiem.util import get_dbconn, noaaport_text


def main(argv):
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()

    cursor.execute(
        """
        SELECT data, entered at time zone 'UTC', pil from products
        WHERE substr(pil, 1, 3) = %s
        and entered > '2020-12-26 12:00+00' and data ~* 'LAT...LON'
        LIMIT 100
    """,
        (argv[1],),
    )
    with open("%s.txt" % (argv[1],), "a") as fh:
        for _i, row in enumerate(cursor):
            print(row[1])
            fh.write(noaaport_text(row[0]))


if __name__ == "__main__":
    main(sys.argv)
