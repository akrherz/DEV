"""Make sure the AFOS database has the text before we delete."""

import sys
from datetime import timezone

from pandas.io.sql import read_sql
from pyiem.nws.product import TextProduct
from pyiem.util import get_dbconn, noaaport_text


def main(argv):
    """Go for this year."""
    year = int(argv[1])
    postgisdb = get_dbconn("postgis")
    afosdb = get_dbconn("afos")
    acursor = afosdb.cursor()
    # Get all our text products.
    df = read_sql(
        f"SELECT report, svs, issue from warnings_{year} ORDER by issue DESC",
        postgisdb,
        index_col=None,
    )
    for _i, row in df.iterrows():
        utcnow = row["issue"].astimezone(timezone.utc)
        text = row["report"]
        # GIGO
        if text.find("\x01") > 0:
            text = text[text.find("\x01") :]
        texts = [noaaport_text(text)]
        if row["svs"] is not None:
            for token in row["svs"].split("__"):
                if token.strip() == "":
                    continue
                texts.append(noaaport_text(token))
        for text in texts:
            try:
                prod = TextProduct(text, utcnow=utcnow, parse_segments=False)
            except Exception as exp:
                print(exp)
                continue
            acursor.execute(
                "SELECT entered from products where pil = %s and source = %s "
                "and entered = %s",
                (prod.afos, prod.source, prod.valid),
            )
            if acursor.rowcount > 0:
                continue
            print(f"Creating afos database entry {prod.get_product_id()}")
            acursor.execute(
                "INSERT into products(entered, source, pil, data, wmo) "
                "VALUES (%s, %s, %s, %s, %s)",
                (prod.valid, prod.source, prod.afos, text, prod.wmo),
            )
    acursor.close()
    afosdb.commit()


if __name__ == "__main__":
    main(sys.argv)
