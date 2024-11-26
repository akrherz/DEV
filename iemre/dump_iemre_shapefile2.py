"""Dump daily precip totals to shapefiles.

NOTE: DBF has a 256 column limit, so we dump twice here.
"""

import datetime

import geopandas as gpd
import netCDF4
import numpy as np
from pyiem import iemre, reference, util
from shapely.geometry import Point


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


def main():
    """Go Main Go"""
    nc = netCDF4.Dataset("/mesonet/data/iemre/2021_iemre_daily.nc")
    nc.variables["p01d_12z"]
    # Compute needed grid bounds
    #     y,  x
    # NW 678, 412
    # SW 313, 417
    # NE 764, 787
    # SE 432, 941
    # (west, east, south, north) = compute_bounds(nc)
    west, south = iemre.find_ij(reference.MW_WEST, reference.MW_SOUTH)
    east, north = iemre.find_ij(reference.MW_EAST, reference.MW_NORTH - 0.1)
    lats = nc.variables["lat"][south:north]
    lons = nc.variables["lon"][west:east]
    lons, lats = np.meshgrid(lons, lats)
    nc.close()
    pts = []
    for lon, lat in zip(np.ravel(lons), np.ravel(lats), strict=False):
        pts.append(Point(lon, lat))
    df = gpd.GeoDataFrame({"geometry": pts})
    for month in range(1, 11):
        print(month)
        nc = netCDF4.Dataset("/mesonet/data/iemre/2021_iemre_daily.nc")
        tidx0 = iemre.daily_offset(datetime.date(2021, month, 1))
        tidx1 = iemre.daily_offset(datetime.date(2021, month + 1, 1))
        tot = np.zeros(lons.shape)
        for idx in range(tidx0, tidx1):
            high = util.c2f(
                nc.variables["high_tmpk"][idx, south:north, west:east] - 273.15
            )
            low = util.c2f(
                nc.variables["low_tmpk"][idx, south:north, west:east] - 273.15
            )
            high = np.where(high > 86, 86, high)
            high = np.where(high < 50, 50, high)
            low = np.where(low < 50, 50, low)
            tot += ((high - 50) + (low - 50)) / 2.0
        df[f"g2021_{month}f"] = np.ravel(tot)
        nc.close()
    df.to_file("gdd.shp")


if __name__ == "__main__":
    main()
