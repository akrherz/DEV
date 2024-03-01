"""Update watches database entry."""

import traceback

import requests

from pyiem.nws.product import TextProduct
from pyiem.util import get_dbconn, noaaport_text


def main():
    """Go Main Go."""
    postgisdb = get_dbconn("postgis")
    cursor = postgisdb.cursor()
    cursor2 = postgisdb.cursor()
    cursor.execute(
        "SELECT report, issued, ctid from watches where "
        "product_id_saw is null and issued > '2005-01-01' and "
        "issued < '2007-01-01' and "
        "report is not null"
    )
    for row in cursor:
        if row[0].find("\n") > 0:
            print(row[1])
            continue
        report = row[0].strip()
        line1 = report[:4]
        pos = report.find("SAW")
        line2 = report[4:pos]
        line3 = report[pos : (pos + 6)]
        newtext = "%s\n%s\n%s\n%s" % (line1, line2, line3, report[(pos + 6) :])

        try:
            prod = TextProduct(newtext, utcnow=row[1])
        except Exception:
            traceback.print_exc()
            continue
        uri = (
            "https://mesonet.agron.iastate.edu/api/1/nwstext/"
            f"{prod.get_product_id()}"
        )
        req = requests.get(uri)
        if req.content.decode("ascii").find("SAW") == -1:
            print(uri)
            with open(f"/tmp/{row[1]:%Y%m%d%H%M}.txt", "w") as fh:
                fh.write(noaaport_text(row[0]))
            continue
        cursor2.execute(
            "UPDATE watches SET product_id_saw = %s where ctid = %s",
            (prod.get_product_id(), row[2]),
        )
    cursor2.close()
    postgisdb.commit()


if __name__ == "__main__":
    main()
