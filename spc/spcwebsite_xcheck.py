"""Scrape the SPC website and verify we have all that data!"""

import time
from datetime import date

import pandas as pd
import requests
from pyiem.nws.product import TextProduct
from pyiem.util import logger, noaaport_text, utc
from tqdm import tqdm

LOG = logger()


def do(progress, dt: date):
    """Process the date!"""
    hr = "11"
    url = (
        f"https://www.spc.noaa.gov/products/outlook/archive/{dt.year}/"
        f"KWNSPTSDY3_{dt:%Y%m%d}{hr}00.txt"
    )
    for attempt in range(3):
        spcreq = requests.get(url, timeout=60)
        if spcreq.status_code >= 500 and attempt < 2:
            progress.write(f"Proxy {spcreq.status_code} for {url}, sleep")
            time.sleep(10)
            continue
        if spcreq.status_code != 200:
            progress.write(f"Got status_code {spcreq.status_code} for {url}")
            return
    # Careful here
    text = f"000 \nWUUS03 KWNS {dt:%d}{hr}00\nPTSDY3\n\n{spcreq.text}"
    utcnow = utc(dt.year, dt.month, dt.day, 20)
    prod = TextProduct(text, utcnow=utcnow, ugc_provider={})
    url = (
        "https://mesonet.agron.iastate.edu/api/1/nwstext/"
        f"{prod.get_product_id()}"
    )
    req = requests.get(url, timeout=60)
    if req.status_code == 200:
        return
    # Careful here
    text = f"000 \nWUUS03 KWNS {prod.valid:%d%H%M}\nPTSDY3\n\n{spcreq.text}"
    localfn = f"prods/{dt:%Y%m%d}.txt"
    progress.write(f"Writing {localfn} cause {prod.get_product_id()}")
    with open(localfn, "w", encoding="utf-8") as fh:
        fh.write(noaaport_text(text))
    with open("cmds_to_run", "a", encoding="utf-8") as fh:
        fh.write(
            (
                f"cat {localfn} | pywwa-parse-afos-dump -x -l "
                f"-u {prod.valid.strftime('%Y-%m-%dT%H:%M')} -s 10\n"
            )
        )
        fh.write(
            (
                f"cat {localfn} | pywwa-parse-spc -x -l "
                f"-u {prod.valid.strftime('%Y-%m-%dT%H:%M')} -s 10\n"
            )
        )


def main():
    """Go Main Go."""
    # progress = tqdm(pd.date_range("2008/03/22", "2026/01/01"))
    progress = tqdm(pd.date_range("2006/01/01", "2026/01/01"))
    for dt in progress:
        progress.set_description(f"{dt:%Y-%m-%d}")
        do(progress, dt)


if __name__ == "__main__":
    main()
