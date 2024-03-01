"""Add more metadata to GAIRMET archive.

per akrherz/pyIEM#628
"""

# stdlib
import datetime

# third party
import requests

from pyiem.nws.products.gairmet import parser
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    conn = get_dbconn("postgis")
    cursor = conn.cursor()
    cursor2 = conn.cursor()
    cursor.execute(
        "SELECT distinct product_id from airmets where product_id ~* 'GMTICE' "
    )
    for row in cursor:
        prodid = row[0]
        text = requests.get(
            f"https://mesonet.agron.iastate.edu/api/1/nwstext/{prodid}"
        ).text
        if text.find("Product not found.") > -1:
            print(f"Failed to fetch {prodid}")
        utcnow = datetime.datetime.strptime(prodid[:12], "%Y%m%d%H%M").replace(
            tzinfo=datetime.timezone.utc
        )
        prod = parser(text, utcnow=utcnow)
        for airmet in prod.data.airmets:
            if not airmet.weather_conditions:
                print(airmet.gml_id)
                print(prodid)
                return
            cursor2.execute(
                "DELETE from airmets where product_id = %s",
                (prodid,),
            )
            cursor2.execute(
                "DELETE from airmet_freezing_levels where product_id = %s",
                (prodid,),
            )
            prod.sql(cursor2)
    cursor2.close()
    conn.commit()


if __name__ == "__main__":
    main()
