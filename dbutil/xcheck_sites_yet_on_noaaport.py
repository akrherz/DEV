"""See what AWX has vs Noaaport."""

import time

import httpx
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    # manually provided by listing in data-curation email list-serv
    with (
        open("/tmp/list.txt", encoding="ascii") as fh,
        httpx.Client() as client,
    ):
        for line in fh:
            tokens = line.split()
            if not tokens:
                continue
            station = tokens[0]
            st4 = station if len(station) == 4 else f"K{station}"
            if len(st4) != 4:
                continue
            url = (
                "https://aviationweather.gov/cgi-bin/data/metar.php?"
                f"ids={st4}&hours=48&order=id%2C-obs&sep=true"
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
                        LOG.warning(f"Failed to fetch {st4} {req.status_code}")
                        continue
                    break
                except Exception as exp:
                    LOG.info("Failed to fetch %s: %s", st4, exp)
            awx = {}
            for line in req.text.split("\n"):
                if line.strip() == "":
                    continue
                awx[line[5:11]] = f"{line}="
            if awx:
                LOG.info("Found %s", st4)


if __name__ == "__main__":
    main()
