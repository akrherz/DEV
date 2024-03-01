"""See akrherz/iem#183"""

import sys

from pyiem.nws.products.vtec import parser
from pyiem.util import get_dbconn, noaaport_text


def main(argv):
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor("streamer")
    cursor2 = pgconn.cursor()

    cursor.execute(
        f"SELECT ctid, report, svs, updated from warnings_{argv[1]} "
        "WHERE svs is not null ORDER by issue"
    )
    considered = 0
    updated = 0
    for row in cursor:
        considered += 1
        ctid = row[0]
        # report = row[1]
        svss = row[2]
        baseupdated = row[3]
        for svs in svss.split("__")[::-1]:
            if svs.strip() == "":
                continue
            try:
                prod = parser(noaaport_text(svs))
            except Exception as exp:
                print(exp)
                sys.exit()
            if prod.valid != baseupdated:
                print("old: %s new: %s" % (baseupdated, prod.valid))
                updated += 1
                cursor2.execute(
                    f"UPDATE warnings_{argv[1]} SET updated = %s "
                    "WHERE ctid = %s",
                    (prod.valid, ctid),
                )
            break
    print("done updated %s rows of %s candidates" % (updated, considered))
    cursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main(sys.argv)
