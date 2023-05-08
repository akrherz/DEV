"""Fix empty product_id."""

# third party
import requests
from psycopg2.extras import RealDictCursor
from tqdm import tqdm

from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=RealDictCursor)
    cursor2 = pgconn.cursor()
    cursor.execute(
        "SELECT ctid, product_issue at time zone 'UTC' as utc_issue, day, "
        "outlook_type from spc_outlook WHERE product_id is null "
    )
    print(f"Found {cursor.rowcount}")
    for row in tqdm(cursor, total=cursor.rowcount):
        if row["outlook_type"] == "C":
            day = "%02i" % (row["day"] if row["day"] < 4 else 48,)
            wmo = f"WUUS{day}"
            pil = "PTSDY%s" % (row["day"],)
            if row["day"] > 3:
                pil = "PTSD48"
        else:
            day = row["day"] if row["day"] < 3 else 8
            wmo = f"FNUS3{day}"
            pil = "PFWFD%s" % (row["day"],)
            if row["day"] > 2:
                pil = "PFWF38"
        product_id = f"{row['utc_issue']:%Y%m%d%H%M}-KWNS-{wmo}-{pil}"
        url = f"https://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
        req = requests.get(url)
        if req.status_code == 200:
            cursor2.execute(
                "UPDATE spc_outlook SET product_id = %s WHERE ctid = %s",
                (product_id, row["ctid"]),
            )
        else:
            print(f"Ruh roh, {product_id} is {req.status_code}")
    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
