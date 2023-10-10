"""Process really old stuff."""
import datetime
import os
import re
import sys

from tqdm import tqdm

from pyiem.nws.product import TextProduct
from pyiem.util import get_dbconn, noaaport_text, utc

# Copied from iem/scripts/util/poker2afos.py
sys.path.insert(0, "/opt/iem/scripts/util")
from poker2afos import XREF_SOURCE  # noqa


def save(prod, cursor):
    """Save this to the database!"""
    if prod.valid.year > 1996 or prod.valid.year < 1993:
        return
    utcnow = prod.valid.astimezone(datetime.timezone.utc)
    table = "products_%s_%s" % (
        utcnow.year,
        "0106" if utcnow.month < 7 else "0712",
    )
    wmo = prod.wmo
    if len(wmo) == 5:
        wmo = "%s0%s" % (wmo[:4], wmo[4])
    cursor.execute(
        f"INSERT into {table} (data, pil, entered, source, wmo) VALUES "
        "(%s, %s, %s, %s, %s)",
        (
            prod.text,
            prod.afos,
            prod.valid,
            XREF_SOURCE.get(prod.source, prod.source),
            wmo,
        ),
    )


def splitter(fn):
    """Generate products."""
    data = open(fn, "rb", encoding="utf8").read().decode("ascii", "ignore")
    tokens = re.split("[0-9]{3} \r\r\n", data)
    for token in tokens:
        product = "000 \r\r\n%s" % (token,)
        product = product.split("\003")[0]
        product = noaaport_text(product).replace("\000", "")
        yield product


def main():
    """Go Main Go."""
    os.chdir("/mesonet/tmp/poker")
    dbconn = get_dbconn("afos")
    for dirpath, _dirnames, filenames in tqdm(os.walk(".")):
        cursor = dbconn.cursor()
        for fn in filenames:
            if not fn.endswith(".gdbm"):
                continue
            date = datetime.datetime.strptime(dirpath[:12], "./%Y/%b%d")
            utcnow = utc(date.year, date.month, date.day)
            for product in splitter(dirpath + "/" + fn):
                try:
                    prod = TextProduct(
                        product, utcnow=utcnow, parse_segments=False
                    )
                    save(prod, cursor)
                except Exception:
                    continue
        cursor.close()
        dbconn.commit()


def test_splitter():
    """Can we make things happen."""
    tokens = list(splitter("/tmp/1113.gdbm"))
    assert len(tokens) == 16


if __name__ == "__main__":
    main()
