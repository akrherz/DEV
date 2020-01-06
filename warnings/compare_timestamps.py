"""Reprocess junky data"""

import pandas as pd
from pyiem.util import noaaport_text, get_dbconn
from pyiem.nws.products.vtec import parser

ISO9660 = "%Y-%m-%d %H:%M"


def main():
    """go"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute(
        """
        SELECT report, issue, wfo, eventid
        from sbw_2019 where
        status = 'NEW' and phenomena = 'SQ' and significance = 'W'
    """
    )

    print("Found %s entries to process..." % (cursor.rowcount,))
    entries = []
    for row in cursor:
        prod = parser(noaaport_text(row[0]), utcnow=row[1])
        vtec_time = prod.segments[0].vtec[0].begints
        mnd_time = prod.valid
        wmo_time = prod.wmo_valid
        if (
            vtec_time != mnd_time
            or vtec_time != wmo_time
            or wmo_time != mnd_time
        ):
            entries.append(
                {
                    "wfo": row[2],
                    "eventid": row[3],
                    "vtec_time": vtec_time.strftime(ISO9660),
                    "mnd_time": mnd_time.strftime(ISO9660),
                    "wmo_time": wmo_time.strftime(ISO9660),
                }
            )

    df = pd.DataFrame(entries)
    with pd.ExcelWriter("sq.xlsx") as writer:
        df.to_excel(writer)


if __name__ == "__main__":
    main()
