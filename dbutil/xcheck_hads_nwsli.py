"""Cross check SHEF ingest with NWSLI and HADS website..."""

import re

import pandas as pd
import requests
from pyiem.database import get_sqlalchemy_conn
from tqdm import tqdm

CSVFN = "/home/akrherz/Downloads/nwsli_database.csv"
NWSLI_RE = re.compile(r"^[A-Z]{4}\d$")


def dowork(progress, row: dict):
    """do work!"""
    nwsli = row["station"]
    # Check 1, is this NWSLIsh
    m = NWSLI_RE.match(nwsli)
    if not m:
        return
    resp = requests.get(
        "https://hads.ncep.noaa.gov/cgi-bin/hads/interactiveDisplays/"
        f"displayMetaData.pl?table=dcp&nwsli={nwsli}",
        timeout=20,
    )
    if "is not available on this web site" not in resp.text:
        progress.write(
            f"{row['pid']} {nwsli} {row['state']} {row['wfo']} {row['name']}"
        )


def main():
    """Go Main Go!"""
    with get_sqlalchemy_conn("iem") as conn:
        udf = pd.read_sql(
            """
    with data as (
        SELECT station, max(product_id) as pid from current_shef where
        strpos(product_id, 'KWOH') > 0 and length(station) = 5
        group by station order by station)
    select station, network, wfo, state, name, pid
    from data d LEFT JOIN stations t
    on (d.station = t.id) order by station
    """,
            conn,
            index_col=None,
        )
    print(f"Found {len(udf.index)} NWSLIsh stations in current_shef")
    df = pd.read_csv(CSVFN, low_memory=False)
    progress = tqdm(udf.iterrows())
    for _idx, row in progress:
        if row["station"] in df["NWSLI"].values:
            continue
        progress.set_description(row["station"])
        dowork(progress, row)


if __name__ == "__main__":
    main()
