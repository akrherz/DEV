"""See what AWX has.

https://aviationweather.gov/data/cache/stations.cache.xml.gz
"""

import time

import httpx
from lxml import etree
from sqlalchemy import text

from pyiem.database import get_sqlalchemy_conn
from pyiem.util import logger

LOG = logger()


def safe(station, key):
    """Safe."""
    val = station.find(key)
    if val is None:
        return "MISSING"
    return val.text


def main():
    """Go Main Go."""
    local = open("/tmp/stations.cache.xml", "rb")
    doc = etree.parse(local)
    with get_sqlalchemy_conn("mesosite") as conn, httpx.Client() as client:
        for station in doc.xpath(".//Station"):
            if not station.xpath("./site_type/METAR"):
                continue
            sid4 = station.find("station_id").text
            sid = sid4[1:] if sid4[0] == "K" else sid4
            res = conn.execute(
                text(
                    "select id from stations where id = :sid and "
                    "network ~* 'ASOS'"
                ),
                {"sid": sid},
            )
            if res.rowcount > 0:
                continue
            url = (
                "https://aviationweather.gov/cgi-bin/data/metar.php?"
                f"ids={sid4}&hours=48&order=id%2C-obs&sep=true"
            )
            attempt = 0
            while attempt < 3:
                attempt += 1
                try:
                    req = client.get(url, timeout=20)
                    if req.status_code == 429:
                        LOG.info("Got 429, cooling jets for 5 seconds.")
                        time.sleep(5)
                        continue
                    if req.status_code != 200:
                        LOG.warning(f"Failed fetch {sid4} {req.status_code}")
                        continue
                    break
                except Exception as exp:
                    LOG.info("Failed to fetch %s: %s", sid4, exp)
            awx = {}
            for line in req.text.split("\n"):
                if line.strip() == "":
                    continue
                awx[line[5:11]] = f"{line}="
            if awx:
                LOG.info(
                    "Found %s %s %s %s %s %s",
                    sid4,
                    safe(station, "site"),
                    safe(station, "state"),
                    safe(station, "country"),
                    safe(station, "latitude"),
                    safe(station, "longitude"),
                )


if __name__ == "__main__":
    main()
