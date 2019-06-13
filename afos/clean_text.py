"""Some products went in the database with some cruft."""
import sys
import re

from pyiem.util import get_dbconn

MYRE = re.compile("[A-Z0-9]{5,6} [A-Z]{4} [0-9]{5,6}")


def main(argv):
    """Go Main Go."""
    table = argv[1]
    pgconn = get_dbconn('afos')
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute("""
        SELECT data, source, wmo, pil, entered from """ + table + """
        ORDER by length(data) ASC
    """)
    updated = 0
    for row in cursor:
        # This line was found to be nearly always bad
        testline = row[0].split("\r\r\n")[-2]
        m = MYRE.search(testline)
        if not m:
            continue
        # update time
        newdata = "\r\r\n".join(row[0].split("\r\r\n")[:-2])
        cursor2.execute("""
            UPDATE """ + table + """ SET data = %s
            WHERE source = %s and wmo = %s and pil = %s and entered = %s
        """, (newdata, row[1], row[2], row[3], row[4]))
        updated += 1
        if updated % 1000 == 0:
            cursor2.close()
            pgconn.commit()
            cursor2 = pgconn.cursor()

    print("updated %s rows" % (updated, ))
    cursor2.close()
    pgconn.commit()


if __name__ == '__main__':
    main(sys.argv)
