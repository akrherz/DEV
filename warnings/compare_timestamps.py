"""Reprocess junky data"""

from pyiem.util import noaaport_text, get_dbconn
from pyiem.nws.products.vtec import parser


def main():
    """go"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute(
        """
        SELECT report, issue, wfo, eventid
        from sbw_2019 where
        status = 'NEW' and phenomena = 'TO' and significance = 'W'
    """
    )

    print("Found %s entries to process..." % (cursor.rowcount,))
    for row in cursor:
        prod = parser(noaaport_text(row[0]), utcnow=row[1])
        vtec_time = prod.segments[0].vtec[0].begints
        mnd_time = prod.valid
        wmo_time = prod.wmo_valid
        if vtec_time != mnd_time:
            print(
                "%s %s vtec:%s mnd:%s" % (row[2], row[3], vtec_time, mnd_time)
            )
        if vtec_time != wmo_time:
            print(
                "%s %s vtec:%s wmo:%s" % (row[2], row[3], vtec_time, wmo_time)
            )
        if wmo_time != mnd_time:
            print("%s %s wmo:%s mnd:%s" % (row[2], row[3], wmo_time, mnd_time))


if __name__ == "__main__":
    main()
