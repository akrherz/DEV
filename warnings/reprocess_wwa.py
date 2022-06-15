"""Reprocess junky data"""
import sys

from pyiem.util import noaaport_text, get_dbconn, logger
from pyiem.nws.products.vtec import parser

LOG = logger()


def p(ts):
    """Helper."""
    if ts is None:
        return "(NONE)"
    return ts.strftime("%Y-%m-%d %H:%M")


def main(argv):
    """go"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()

    table = f"warnings_{argv[1]}"

    cursor.execute(
        f"SELECT ctid, report, svs, ugc from {table} where "
        "purge_time is null"
    )

    LOG.info("Found %s entries to process...", cursor.rowcount)
    for row in cursor:
        ctid = row[0]
        report = row[1]
        svs = row[2]
        ugc = row[3]
        if svs is not None and svs != "":
            for token in svs.split("__"):
                if len(token) > 100:
                    report = token
        try:
            prod = parser(noaaport_text(report))
        except Exception as exp:
            LOG.info("%s: %s", ctid, exp)
            continue
        for segment in prod.segments:
            if ugc in [str(s) for s in segment.ugcs]:
                cursor2.execute(
                    f"UPDATE {table} set purge_time = %s WHERE ctid = %s",
                    (segment.ugcexpire, ctid),
                )

    cursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main(sys.argv)
