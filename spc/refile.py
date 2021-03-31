"""Refile contents of the database."""

from psycopg2.extras import RealDictCursor
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=RealDictCursor)
    cursor2 = pgconn.cursor()
    cursor.execute(
        "SELECT issue, product_issue, expire, threshold, category, day, "
        "outlook_type, geom, product_id, updated from spc_outlooks "
        "ORDER by product_issue ASC"
    )
    for row in cursor:
        cursor2.execute(
            "SELECT id from spc_outlook where product_issue = %s and day = %s "
            "and outlook_type = %s",
            (row["product_issue"], row["day"], row["outlook_type"]),
        )
        if cursor2.rowcount == 0:
            cursor2.execute(
                "INSERT into spc_outlook(issue, product_issue, expire, "
                "updated, product_id, outlook_type, day) VALUES "
                "(%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (
                    row["issue"],
                    row["product_issue"],
                    row["expire"],
                    row["updated"],
                    row["product_id"],
                    row["outlook_type"],
                    row["day"],
                ),
            )
        outlook_id = cursor2.fetchone()[0]
        cursor2.execute(
            "INSERT into spc_outlook_geometries(spc_outlook_id, threshold, "
            "category, geom) VALUES (%s, %s, %s, %s)",
            (outlook_id, row["threshold"], row["category"], row["geom"]),
        )

    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
