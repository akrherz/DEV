"""Lapse"""

import datetime

import requests
from bs4 import BeautifulSoup


def main():
    """Go Main"""
    now = datetime.datetime(2026, 8, 1, 0, 0)
    ets = datetime.datetime(2026, 8, 14, 0, 0)
    interval = datetime.timedelta(minutes=1440)

    stepi = 0
    while now < ets:
        uri = now.strftime(
            (
                "http://mtarchive.geol.iastate.edu/%Y/%m/%d/cod/sat/goes19/"
                "continental/conus/abi10/"
            )
        )
        req = requests.get(uri, timeout=30)
        # Find all the HTML links in the page
        soup = BeautifulSoup(req.content, "html.parser")
        for link in soup.find_all("a")[::5]:
            href = link.get("href")
            if href and href.endswith(".jpg"):
                req = requests.get(uri + href, timeout=30)
                with open(f"images/{stepi:05.0f}.jpg", "wb") as fp:
                    fp.write(req.content)
                stepi += 1

        now += interval


if __name__ == "__main__":
    main()
