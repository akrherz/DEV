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
        WHERE pil = %s
        and entered >= '2020-02-26 12:00+00'
        ORDER by entered ASC
    """,
        (argv[1],),
    )
    with open("%s.txt" % (argv[1],), "a") as fh:
        for _i, row in enumerate(cursor):
            fh.write(noaaport_text(row[0]))


if __name__ == "__main__":
    main(sys.argv)
