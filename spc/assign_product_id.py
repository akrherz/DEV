"""Fix empty product_id."""

# third party
import httpx
from tqdm import tqdm

from pyiem.database import get_dbconnc
from pyiem.nws.product import TextProduct


def main():
    """Go Main Go."""
    pgconn, cursor = get_dbconnc("postgis")
    cursor2 = pgconn.cursor()
    cursor.execute(
        "SELECT ctid, raw, issue from sigmets_archive "
        "WHERE product_id is null and strpos(raw, E'\001') = 1"
    )
    print(f"Found {cursor.rowcount}")
    updates = 0
    for row in tqdm(cursor, total=cursor.rowcount):
        try:
            prod = TextProduct(row["raw"], utcnow=row["issue"])
        except Exception as exp:
            print(f"Failed to parse {row['ctid']} {exp}")
            continue
        product_id = prod.get_product_id()
        url = f"https://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
        req = httpx.get(url)
        if req.status_code == 200:
            cursor2.execute(
                "UPDATE sigmets_archive SET product_id = %s WHERE ctid = %s",
                (product_id, row["ctid"]),
            )
            updates += 1
            if updates % 100 == 0:
                cursor2.close()
                pgconn.commit()
                cursor2 = pgconn.cursor()
        else:
            print(f"Ruh roh, {product_id} is {req.status_code}")
    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
