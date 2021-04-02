"""Scrape the SPC website and verify we have all that data!"""

# Third party
from pyiem.util import logger, utc, noaaport_text
from pyiem.nws.product import TextProduct
import pandas as pd
import requests

LOG = logger()


def do(date):
    """Process the date!"""
    hr = "13"
    url = (
        f"https://www.spc.noaa.gov/products/outlook/archive/{date.year}/"
        f"KWNSPTSDY1_{date.strftime('%Y%m%d')}{hr}00.txt"
    )
    req = requests.get(url)
    if req.status_code != 200:
        LOG.info("Got status_code %s for %s", req.status_code, url)
        return
    text = (
        f"000 \nWUUS01 KWNS {date.strftime('%d')}{hr}00\nPTSDY1\n\n" + req.text
    )
    utcnow = utc(date.year, date.month, date.day, 20)
    prod = TextProduct(text, utcnow=utcnow)
    url = (
        "https://mesonet.agron.iastate.edu/api/1/nwstext/"
        f"{prod.get_product_id()}"
    )
    req = requests.get(url)
    if req.status_code == 200:
        return
    localfn = f"prods/{date.strftime('%Y%m%d')}.txt"
    LOG.info("Writing %s", localfn)
    with open(localfn, "w") as fh:
        fh.write(noaaport_text(text))
    with open("cmds_to_run", "a") as fh:
        fh.write(
            (
                f"cat {localfn} | python parsers/afos_dump.py -x -l "
                f"-u {utcnow.strftime('%Y-%m-%dT%H:%M')}\n"
            )
        )
        fh.write(
            (
                f"cat {localfn} | python parsers/spc_parser.py -x -l "
                f"-u {utcnow.strftime('%Y-%m-%dT%H:%M')}\n"
            )
        )


def main():
    """Go Main Go."""
    for date in pd.date_range("2017/10/11", "2017/10/12"):
        do(date)


if __name__ == "__main__":
    main()
