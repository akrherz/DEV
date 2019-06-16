"""Send products from AFOS database to pyWWA."""

from pyiem.util import get_dbconn, noaaport_text


def main():
    """Go Main Go."""
    pgconn = get_dbconn('afos')
    cursor = pgconn.cursor('streamer')

    fp = open('SWOMCD.txt', 'w')

    cursor.execute("""
        SELECT data from products
        WHERE pil = 'SWOMCD' and entered < '2008-10-21 15:34'
        ORDER by entered ASC
    """)
    for _i, row in enumerate(cursor):
        fp.write(noaaport_text(row[0]))
    fp.close()


if __name__ == '__main__':
    main()
