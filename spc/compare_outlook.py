"""Compare IEM vs SPC, to see who is better!"""
import subprocess
import datetime

import requests
import pandas as pd
import geopandas as gpd
import pytz
from pyiem.util import get_dbconnstr, logger, utc

LOG = logger()
BASEURL = "https://www.spc.noaa.gov/products/outlook/archive"
CANONICAL = {
    # 1: "0100",
    # 6: "1200",
    # 7: "0700",  # 2
    8: "0830",
    # 13: "1300",
    # 16: "1630",
    # 17: "1730",  # 2
    # 20: "2000",
}
DAY = 3
PIL = "PTSDY3"


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
    label = CANONICAL[cycle]
    if cycle == 7:
        lts = valid.astimezone(pytz.timezone("America/Chicago"))
        if lts.dst():
            label = "0600"
    if cycle == 8:
        lts = valid.astimezone(pytz.timezone("America/Chicago"))
        if lts.dst():
            label = "0730"
    uri = valid.strftime(
        f"{BASEURL}/%Y/day{DAY}otlk_%Y%m%d_{label}_cat.lyr.geojson"
    )
    try:
        spc = gpd.read_file(uri)
    except Exception as exp:
        LOG.info("Failed fetching %s with %s", uri, exp)
        return False
    dbvalid = valid + datetime.timedelta(days=(DAY - 1))
    iem = gpd.read_postgis(
        "SELECT threshold, category, geom, product_id from "
        "spc_outlook_geometries g JOIN "
        "spc_outlook o on (g.spc_outlook_id = o.id) WHERE outlook_type = 'C' "
        f"and date(issue at time zone 'UTC') = '{dbvalid:%Y-%m-%d}' and "
        "day = %s and cycle = %s and "
        "category = 'CATEGORICAL'",
        get_dbconnstr("postgis"),
        params=(DAY, cycle),
        geom_col="geom",
    )
    for _idx, row in spc.iterrows():
        if row["LABEL"] == "":
            continue
        iemrow = iem[iem["threshold"] == row["LABEL"]]
        spc_size = row["geometry"].area
        if iemrow.empty:
            iem_size = -1
            product_id = f"{row['ISSUE']}-KWNS-WUUS0{DAY}-{PIL}"
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
    for date in pd.date_range("2019/11/01", "2021/07/07"):
        valid = utc(date.year, date.month, date.day)
        for cycle in CANONICAL:
            if run(valid, cycle, False):
                run(valid, cycle, True)


if __name__ == "__main__":
    main()
