"""Dump daily precip totals to shapefiles.

NOTE: DBF has a 256 column limit, so we dump twice here.
"""
import datetime
import shutil
import sys

import netCDF4
import numpy as np

import geopandas as gpd
import pandas as pd
from pyiem import iemre, reference, util
from pyiem.datatypes import distance
from shapely.geometry import Point

LOG = util.logger()


def compute_bounds(nc):
    """Figure out what is needed for a grid bounds for stage IV"""
    lats = nc.variables["lat"][:]
    lons = nc.variables["lon"][:]
    for lon, lat in [
        [reference.MW_WEST, reference.MW_NORTH],
        [reference.MW_WEST, reference.MW_SOUTH],
        [reference.MW_EAST, reference.MW_NORTH],
        [reference.MW_EAST, reference.MW_SOUTH],
    ]:
        dist = ((lons - lon) ** 2 + (lats - lat) ** 2) ** 0.5
        print(np.unravel_index(dist.argmin(), dist.shape))


def main(argv):
    """Go Main Go"""
    year = int(argv[1])
    # Need to use hourly as we want calendar day totals
    nc = netCDF4.Dataset(f"/mesonet/data/stage4/{year}_stage4_hourly.nc")
    precip = nc.variables["p01m"]
    # Compute needed grid bounds
    #     y,  x
    # NW 678, 412
    # SW 313, 417
    # NE 764, 787
    # SE 432, 941
    # (west, east, south, north) = compute_bounds(nc)
    south = 313
    north = 678
    west = 412
    east = 900
    lats = nc.variables["lat"][south:north, west:east]
    lons = nc.variables["lon"][south:north, west:east]
    pts = []
    for lon, lat in zip(np.ravel(lons), np.ravel(lats)):
        pts.append(Point(lon, lat))
    for m1, m2 in [(1, 8), (9, 12)]:
        # iterate over days
        now = datetime.date(year, m1, 1)
        ets = datetime.date(year, m2, 31)
        cols = {"geometry": pts}
        for dt in pd.date_range(now, ets).strftime("%b%d"):
            cols[dt] = 0
        df = gpd.GeoDataFrame(cols)
        while now <= ets:
            valid = util.utc(now.year, now.month, now.day, 5)
            tidx0 = iemre.hourly_offset(valid)
            now += datetime.timedelta(days=1)
            valid = util.utc(now.year, now.month, now.day, 5)
            tidx1 = iemre.hourly_offset(valid)
            if now.strftime("%m%d") == "1231":
                tidx1 = -1
            data = precip[tidx0:tidx1, south:north, west:east]
            total = np.sum(data, axis=0)
            LOG.info(
                "Processing %s max precip: %.2f",
                now - datetime.timedelta(days=1),
                np.max(total),
            )
            df[(now - datetime.timedelta(days=1)).strftime("%b%d")] = distance(
                np.ravel(total), "MM"
            ).value("IN")
        fn = f"combined{year}_{m1:02.0f}{m2:02.0f}"
        df.to_file(f"{fn}.shp")
        shutil.copyfile("/opt/iem/data/gis/meta/4326.prj", f"{fn}.prj")
    nc.close()


if __name__ == "__main__":
    main(sys.argv)
