"""Look through NCEI ANX files and insert into AFOS database.

https://www.ncei.noaa.gov/data/service-records-retention-system/access/
"""

import os

from sqlalchemy import text

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.product import TextProduct
from pyiem.util import logger

LOG = logger()


def process(pgconn, utcnow, raw):
    """Ingest."""
    raw = f"000 \n{raw}\n"
    prod = TextProduct(raw, utcnow=utcnow)
    # Life choices were made here
    if prod.afos is None:
        return
    res = pgconn.execute(
        text(
            "select data from products where pil = :pil and "
            "entered = :valid and bbb is not distinct from :bbb"
        ),
        {"pil": prod.afos, "valid": prod.valid, "bbb": prod.bbb},
    )
    if res.rowcount > 0:
        return
    LOG.info("Inserting %s", prod.get_product_id())
    pgconn.execute(
        text(
            "INSERT into products (data, pil, entered, source, wmo, "
            "bbb) VALUES (:data, :pil, :entered, :source, :wmo, :bbb)"
        ),
        {
            "data": raw.replace("\r", ""),
            "pil": prod.afos,
            "entered": prod.valid,
            "source": prod.source,
            "wmo": prod.wmo,
            "bbb": prod.bbb,
        },
    )


def readfile(filename, utcnow):
    """Go Main Go."""
    print(f"Processing {filename}")
    with open(filename, "rb") as fh, get_sqlalchemy_conn("afos") as pgconn:
        for token in fh.read().decode("ascii", "ignore").split("****\n"):
            lines = token.split("\n")
            if len(lines) < 4:
                continue
            if lines[0].startswith(("FTAK", "FTPA", "FTUS", "FTPQ")):
                process(pgconn, utcnow, "\n".join(lines[:-1]))
        pgconn.commit()


def main():
    """Go Main Go."""
    for dt in pd.date_range("2010/01/01", "2011/01/01", freq="1h", tz="UTC"):
        ddir = f"/mesonet/tmp/ncei/{dt:%Y/%m/%d/%H}"
        if not os.path.isdir(ddir):
            continue
        utcnow = dt + pd.Timedelta("2 hour")
        for fn in os.listdir(ddir):
            if fn.endswith(".ANX"):
                readfile(f"{ddir}/{fn}", utcnow)


if __name__ == "__main__":
    main()
