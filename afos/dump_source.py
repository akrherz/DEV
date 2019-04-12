"""Send products from AFOS database to pyWWA"""

from pyiem.util import get_dbconn, noaaport_text


def main():
    """Go Main Go."""
    pgconn = get_dbconn('afos')
    acursor = pgconn.cursor('streamer')

    acursor.execute("""
        SELECT pil, entered at time zone 'UTC', source, pil, data
        from products_2017_0712
        WHERE source = 'TJSJ' and entered >= '2017-08-26'
        and entered < '2017-09-13'
    """)
    for row in acursor:
        fn = "TJSJ/%s_%s.txt" % (row[0].strip(), row[1].strftime("%Y%m%d%H%M"))
        o = open(fn, 'a')
        o.write(noaaport_text(row[4]))
        o.write('\r\r\n\003')
        o.close()

    o.close()


if __name__ == '__main__':
    main()
