"""Suck in what WPC's website has to offer."""

import os
import zipfile
from datetime import datetime, timezone

import requests

import geopandas as gpd
import pandas as pd
from pyiem.util import get_dbconn, logger
from shapely.geometry import MultiPolygon

LOG = logger()
COMBOS = [
    (1, 1),
    (1, 8),
    (1, 9),
    (1, 16),
    (2, 9),
    (2, 21),
    (3, 9),
    (3, 21),
]
PREFIX = {1: "94e", 2: "98e", 3: "99e"}


def get_threshold(val):
    """Blah"""
    if val.lower().startswith("marginal"):
        return "MRGL"
    if val.lower().startswith("slight"):
        return "SLGT"
    if val.lower().startswith("moderate"):
        return "MDT"
    if val.lower().startswith("enhanced"):
        return "ENH"
    if val.lower().startswith("high"):
        return "HIGH"


def process(cursor, zipfn, date, day, hr):
    """Do magic."""
    uri = f"https://www.wpc.ncep.noaa.gov/archives/ero/{date:%Y%m%d}/{zipfn}"
    req = requests.get(uri, timeout=30)
    if req.status_code != 200:
        LOG.info("Got %s for %s", req.status_code, uri)
        return
    with open(zipfn, "wb") as fh:
        fh.write(req.content)
    zfp = zipfile.ZipFile(zipfn)
    names = []
    shpfn = None
    for name in zfp.namelist():
        with open(name, "wb") as fp:
            fp.write(zfp.read(name))
        names.append(name)
        if name.endswith(".shp"):
            shpfn = name
    df = gpd.read_file(shpfn)
    # print(df.columns)
    for fn in names:
        os.unlink(fn)
    os.unlink(zipfn)

    issue = datetime.strptime(df.iloc[0]["START_TIME"], "%Y-%m-%d %H:%M:%S")
    issue = issue.replace(tzinfo=timezone.utc)
    expire = datetime.strptime(df.iloc[0]["END_TIME"], "%Y-%m-%d %H:%M:%S")
    expire = expire.replace(tzinfo=timezone.utc)
    pissue = datetime.strptime(df.iloc[0]["ISSUE_TIME"], "%Y-%m-%d %H:%M:%S")
    pissue = pissue.replace(tzinfo=timezone.utc)
    cycle = hr
    if day == 1 and hr == 9:
        cycle = 8

    cursor.execute(
        "SELECT id from spc_outlook where product_issue = %s and day = %s and "
        "outlook_type = 'E' and issue = %s and expire = %s",
        (pissue, day, issue, expire),
    )
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT into spc_outlook (issue, product_issue, expire, "
            "outlook_type, day, cycle, product_id) VALUES "
            "(%s, %s, %s, 'E', %s, %s, 'SHAPEFILE') "
            "returning id",
            (issue, pissue, expire, day, cycle),
        )
        oid = cursor.fetchone()[0]
    else:
        oid = cursor.fetchone()[0]
        cursor.execute(
            "DELETE from spc_outlook_geometries where spc_outlook_id = %s",
            (oid,),
        )
    geoms = {}
    for _i, row in df.iterrows():
        outlook = row["OUTLOOK"]
        if outlook.startswith("None"):
            continue
        threshold = get_threshold(row["OUTLOOK"])
        if not row["geometry"].is_valid:
            row["geometry"] = row["geometry"].buffer(0)
            if not row["geometry"].is_valid:
                LOG.info("invalid geometry!")
                continue
        arr = geoms.setdefault(threshold, [])
        if isinstance(row["geometry"], MultiPolygon):
            arr.extend(row["geometry"].geoms)
        else:
            arr.append(row["geometry"])
    for threshold, arr in geoms.items():
        mp = MultiPolygon(arr)
        cursor.execute(
            "INSERT into spc_outlook_geometries (spc_outlook_id, threshold, "
            "category, geom) VALUES (%s, %s, %s, "
            "ST_SetSRID(ST_Multi(ST_GeomFromText(%s)), 4326) )",
            (oid, threshold, "CATEGORICAL", mp.wkt),
        )


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    for date in pd.date_range("2019/01/04", "2021/07/13"):
        LOG.info("Processing %s", date)
        for day, hr in COMBOS:
            zipfn = f"shp_{PREFIX[day]}_{date:%Y%m%d}{hr:02.0f}.zip"
            cursor = pgconn.cursor()
            process(cursor, zipfn, date, day, hr)
            cursor.close()
            pgconn.commit()


if __name__ == "__main__":
    main()
