"""Sigh."""

import httpx
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper


def main():
    """GO Main."""
    with get_sqlalchemy_conn("mesosite") as conn:
        xref = pd.read_sql(
            sql_helper(
                "select id, synop from stations where network = 'RAOB' "
                "and synop is not null"
            ),
            conn,
        )
    url = (
        "https://www.ncei.noaa.gov/data/integrated-global-radiosonde-archive/"
        "doc/igra2-station-list.txt"
    )
    resp = httpx.get(url)
    for line in resp.text.split("\n"):
        if not line.startswith("USM"):
            continue
        synop = int(line[6:11])
        eyear = int(line[77:81])
        if eyear < 2020:
            continue
        if synop not in xref["synop"].values:
            print(line)


if __name__ == "__main__":
    main()
