"""Make sure our database storage of expiration time is right"""
import sys

from pyiem.util import get_dbconn
from pyiem.nws.products.vtec import parser


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()

    table = "sbw_%s" % (sys.argv[1],)

    cursor.execute("""SET TIME ZONE 'UTC'""")
    cursor.execute(
        f"""
    SELECT report, expire from {table} where
    status = 'CAN' and polygon_end != expire
    and phenomena in ('TO', 'SV')
    """
    )

    for row in cursor:
        prod = parser(row[0])
        if not prod.is_single_action():
            continue
        vtec = prod.segments[0].vtec[0]
        cursor2.execute(
            f"""UPDATE {table} SET expire = %s
                    where %s <= expire and wfo = %s and phenomena = %s
                    and significance = %s and eventid = %s
        """,
            (
                prod.valid,
                prod.valid,
                vtec.office,
                vtec.phenomena,
                vtec.significance,
                vtec.etn,
            ),
        )
        print("%s -> %s rows:%s" % (row[1], prod.valid, cursor2.rowcount))

    print("%s Processed %s rows" % (sys.argv[1], cursor.rowcount))

    cursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
