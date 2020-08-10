"""Old products had no PILs."""
import sys

from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor3 = pgconn.cursor()
    table = argv[1]
    cursor.execute(
        f"SELECT distinct source from {table} "
        "WHERE substr(source, 1, 1) in ('K', 'P') ORDER by source DESC"
    )
    for row in cursor:
        source = row[0]
        print("Processing %s" % (source,))
        # Find wmos with null pils
        cursor2.execute(
            f"SELECT distinct wmo from {table} WHERE "
            "source = %s and pil is null",
            (source,),
        )
        for row2 in cursor2:
            # Lookup over all the data for pils
            cursor3.execute(
                """
                SELECT distinct pil from products WHERE source = %s
                and wmo = %s and pil is not null
            """,
                (source, row2[0]),
            )
            # If one result, we have a winner
            if cursor3.rowcount != 1:
                res = [x[0][:3] for x in cursor3.fetchall()]
                if res and res.count(res[0]) == len(res):
                    pil = "%s%s" % (res[0], source[1:])
                    print("%s %s ambigous to %s" % (source, row2[0], pil))
                else:
                    continue
            else:
                pil = cursor3.fetchone()[0]
            cursor4 = pgconn.cursor()
            cursor4.execute(
                """
                UPDATE products SET pil = %s WHERE
                source = %s and wmo = %s and pil is null
                and entered < '1997-01-01 00:00+00'
            """,
                (pil, source, row2[0]),
            )
            print(
                "%s %s updated %s rows to %s"
                % (source, row2[0], cursor4.rowcount, pil)
            )
            cursor4.close()
            pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
