"""see akrherz/iem#191

Dedup some duplicated FFWs in the warnings table."""
import sys

from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main(argv):
    """Go for this year."""
    year = int(argv[1])
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    table = "sbw_%s" % (year,)
    wtable = "warnings_%s" % (year,)
    # Candidates should have more than one database entry
    # matching issue times
    # matching geom areas (slight hack)
    df = read_sql(
        f"""
        SELECT wfo, eventid, max(oid) as max_oid,
        count(*) from {table} WHERE
        phenomena = 'FF' and significance = 'W' and status = 'NEW'
        GROUP by wfo, eventid HAVING count(*) > 1 and
        min(issue) = max(issue) and max(st_area(geom)) = min(st_area(geom))
    """,
        pgconn,
        index_col=None,
    )
    print("%s entries for dedup found for %s" % (len(df.index), table))
    for _, row in df.iterrows():
        print("  %s %03i is a dup" % (row["wfo"], row["eventid"]))
        cursor.execute(
            f"DELETE from {table} WHERE oid = %s", (row["max_oid"],)
        )
        print("    - removed %s rows from %s" % (cursor.rowcount, table))
        df2 = read_sql(
            f"""
            SELECT ugc, max(oid) as max_oid from {wtable}
            WHERE wfo = %s and phenomena = 'FF' and significance = 'W'
            and eventid = %s GROUP by ugc HAVING count(*) > 1
        """,
            pgconn,
            params=(row["wfo"], row["eventid"]),
        )
        for __, row2 in df2.iterrows():
            cursor.execute(
                f"DELETE from {wtable} WHERE oid = %s", (row2["max_oid"],)
            )
            print(
                "    - removed %s rows for %s in %s"
                % (cursor.rowcount, row2["ugc"], wtable)
            )

    if len(argv) == 2:
        print("NOOP, run with an additional arg to commit")
        return
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
