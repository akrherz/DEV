"""old pywwa helper."""

import datetime
import sys

from pyiem.nws.products.vtec import parser
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    POSTGIS = get_dbconn("postgis")
    cursor = POSTGIS.cursor()
    cursor2 = POSTGIS.cursor()

    table = "warnings_%s" % (sys.argv[1],)

    cursor.execute(
        f"SELECT oid, report, fcster, issue, phenomena, ugc from {table} "
        "where init_expire = issue"
    )

    # running = 0
    # lastugc = None
    for row in cursor:
        oid = row[0]
        report = row[1]
        # issue = row[3]
        try:
            prod = parser(report)
        except Exception as exp:
            print("ERROR, oid: %s exp: %s" % (oid, exp))
            continue
        for seg in prod.segments:
            found = False
            for ugc in seg.ugcs:
                if str(ugc) == row[5]:
                    found = True
            if not found:
                continue
            for vtec in seg.vtec:
                if vtec.phenomena == row[4]:
                    print("HERE!", vtec, vtec.endts)
                    if vtec.endts is None:
                        if vtec.begints is None:
                            vtec.endts = prod.valid + datetime.timedelta(
                                days=1
                            )
                        else:
                            vtec.endts = vtec.begints + datetime.timedelta(
                                days=1
                            )
                    cursor2.execute(
                        """UPDATE """
                        + table
                        + """ SET init_expire = %s
                    where oid = %s""",
                        (vtec.endts, oid),
                    )

    print("%s Processed %s rows" % (sys.argv[1], cursor.rowcount))

    cursor2.close()
    POSTGIS.commit()
    POSTGIS.close()


if __name__ == "__main__":
    main()
