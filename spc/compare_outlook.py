"""Compare IEM vs SPC, to see who is better!"""
import subprocess

import requests
import pandas as pd
import geopandas as gpd
from pyiem.util import get_dbconn, logger

LOG = logger()
BASEURL = "https://www.spc.noaa.gov/products/outlook/archive"
CANONICAL = {
    1: "0100",
    6: "1200",
    13: "1300",
    16: "1630",
    20: "2000",
}


def reprocess(product_id, valid):
    """Send this product_id back through the meatgrinder."""
    req = requests.get(
        f"https://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
    )
    tmpfn = f"/tmp/{product_id}.txt"
    with open(tmpfn, "wb") as fh:
        fh.write(req.content)
    cmd = f"python ~/projects/pyWWA/util/make_text_noaaportish.py {tmpfn}"
    subprocess.call(cmd, shell=True)
    cmd = (
        f"cat {tmpfn} | python ~/projects/pyWWA/parsers/spc_parser.py -x "
        f"-u {valid.strftime('%Y-%m-%dT00:00Z')}"
    )
    subprocess.call(cmd, shell=True)


def run(valid, cycle, secondtrip):
    """Do the comparison for a given valid time."""
    uri = valid.strftime(
        f"{BASEURL}/%Y/day1otlk_%Y%m%d_{CANONICAL[cycle]}_cat.lyr.geojson"
    )
    try:
        spc = gpd.read_file(uri)
    except Exception as exp:
        LOG.info("Failed fetching %s with %s", uri, exp)
        return False
    iem = gpd.read_postgis(
        "SELECT threshold, category, geom, product_id from "
        "spc_outlook_geometries g JOIN "
        "spc_outlook o on (g.spc_outlook_id = o.id) WHERE outlook_type = 'C' "
        f"and date(issue at time zone 'UTC') = '{valid:%Y-%m-%d}' and "
        "day = 1 and cycle = %s and "
        "category = 'CATEGORICAL'",
        get_dbconn("postgis"),
        params=(cycle,),
        geom_col="geom",
    )
    for idx, row in spc.iterrows():
        if row["LABEL"] == "":
            continue
        iemrow = iem[iem["threshold"] == row["LABEL"]]
        spc_size = row["geometry"].area
        if iemrow.empty:
            iem_size = -1
            product_id = f"{row['ISSUE']}-KWNS-WUUS01-PTSDY1"
            LOG.info("setting product_id to %s", product_id)
        else:
            product_id = iemrow["product_id"].iloc[0]
            iem_size = iemrow["geom"].area.iloc[0]
        if 0.99 < (spc_size / iem_size) < 1.01:
            continue
        print(
            f"{valid}[{cycle}] {row['LABEL']} "
            f"SPC: {row['ISSUE']} IEM: {product_id} "
            f"SPC:{spc_size} IEM:{iem_size} secondtrip: {secondtrip}"
        )
        if not secondtrip and product_id is not None:
            reprocess(product_id, valid)
            return True
    return False


def main():
    """Go Main Go."""
    for date in pd.date_range("2020/03/08", "2021/05/17"):
        for cycle in CANONICAL:
            if run(date, cycle, False):
                run(date, cycle, True)


if __name__ == "__main__":
    main()
