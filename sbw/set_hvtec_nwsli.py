"""See akrherz/iem#247"""

import sys

from tqdm import tqdm

from pyiem.nws.products.vtec import parser
from pyiem.util import get_dbconn, noaaport_text


def main(argv):
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()

    table = f"sbw_{argv[1]}"
    table2 = f"warnings_{argv[1]}"

    cursor.execute(
        f"""
        SELECT report, status, wfo, eventid, significance, phenomena,
        updated, polygon_begin from {table}
        WHERE phenomena in ('FA', 'FF', 'FL', 'HY', 'IJ')
        ORDER by polygon_begin ASC
    """
    )
    considered = 0
    desc = tqdm(cursor, total=cursor.rowcount)
    for row in desc:
        desc.set_description(row[7].strftime("%b %d"))
        considered += 1
        try:
            prod = parser(noaaport_text(row[0]))
        except Exception as exp:
            print(exp)
            sys.exit()
        found = False
        for seg in prod.segments:
            if not seg.vtec:
                continue
            v = seg.vtec[0]
            if (
                v.phenomena == row[5]
                and v.significance == row[4]
                and v.etn == row[3]
            ):
                cursor2.execute(
                    f"""
                    UPDATE {table} SET hvtec_severity = %s, hvtec_cause= %s,
                    hvtec_record = %s
                    WHERE wfo = %s and phenomena = %s and significance = %s
                    and status = %s and eventid = %s and updated = %s
                    and polygon_begin = %s
                """,
                    (
                        seg.get_hvtec_severity(),
                        seg.get_hvtec_cause(),
                        seg.get_hvtec_record(),
                        row[2],
                        row[5],
                        row[4],
                        row[1],
                        row[3],
                        row[6],
                        row[7],
                    ),
                )
                found = True
                if cursor2.rowcount == 0:
                    print(prod)
                    print(row)
                    print(cursor2.rowcount)
                    sys.exit()
                if v.action != "NEW":
                    continue
                cursor2.execute(
                    f"""
                    UPDATE {table2} SET hvtec_severity = %s, hvtec_cause= %s,
                    hvtec_record = %s
                    WHERE wfo = %s and phenomena = %s and significance = %s
                    and eventid = %s
                """,
                    (
                        seg.get_hvtec_severity(),
                        seg.get_hvtec_cause(),
                        seg.get_hvtec_record(),
                        row[2],
                        row[5],
                        row[4],
                        row[3],
                    ),
                )
                if cursor2.rowcount == 0:
                    print(prod)
                    print(row)
                    print(cursor2.rowcount)
                    sys.exit()
        if considered % 1000 == 0:
            cursor2.close()
            pgconn.commit()
            cursor2 = pgconn.cursor()
        if not found:
            print(prod)
            sys.exit()
    print("Processed %s rows" % (considered,))
    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
