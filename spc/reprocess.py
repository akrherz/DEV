"""Fix cycle."""

# third party
import requests
from tqdm import tqdm
from psycopg2.extras import RealDictCursor
from pyiem.util import get_dbconn
from pyiem.nws.products.spcpts import parser, _sql_cycle_canonical


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, product_id, product_issue, day from spc_outlook "
        "WHERE cycle = -1 "
    )
    print(f"Found {cursor.rowcount}")
    for row in tqdm(cursor, total=cursor.rowcount):
        url = (
            "https://mesonet.agron.iastate.edu/api/1/nwstext/"
            f"{row['product_id']}"
        )
        req = requests.get(url)
        try:
            prod = parser(req.text, utcnow=row["product_issue"])
        except Exception:
            print("EXP")
            continue
        collect = prod.outlook_collections[row["day"]]
        cursor2 = pgconn.cursor(cursor_factory=RealDictCursor)
        _sql_cycle_canonical(prod, cursor2, row["day"], collect, row["id"])
        cursor2.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
