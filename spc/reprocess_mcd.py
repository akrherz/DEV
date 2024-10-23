"""Update MCDs per corrections."""

import httpx
from pyiem.database import get_dbconnc
from pyiem.nws.products import mcd


def main():
    """Go Main Go."""
    pgconn, cursor = get_dbconnc("postgis")
    cursor2 = pgconn.cursor()
    cursor.execute(
        """
        select year, num, max(product_id), max(issue) as maxtime from mcd
        GROUP by year, num having count(*) > 1
        """,
    )
    for row in cursor:
        text = httpx.get(
            f"https://mesonet.agron.iastate.edu/api/1/nwstext/{row['max']}"
        ).text
        try:
            prod = mcd.parser(text, utcnow=row["maxtime"])
        except Exception as exp:
            print(row["max"], exp)
            continue
        if prod.is_correction and row["maxtime"].year == prod.valid.year:
            prod.database_save(cursor2)
            cursor2.close()
            pgconn.commit()
            cursor2 = pgconn.cursor()
    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
