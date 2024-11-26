"""Dump daily precip totals to shapefiles.

NOTE: DBF has a 256 column limit, so we dump twice here.
"""

import geopandas as gpd
import netCDF4
import numpy as np
from pyiem import reference
from pyiem.datatypes import distance
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
    nc = netCDF4.Dataset("/mesonet/data/stage4/stage4_dailyc.nc")
    precip = nc.variables["p01d_12z"]
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
    for lon, lat in zip(np.ravel(lons), np.ravel(lats), strict=False):
        pts.append(Point(lon, lat))
    df = gpd.GeoDataFrame({"geometry": pts})
    data = precip[:, south:north, west:east]
    total = np.sum(data, axis=0)
    df["prec_in"] = distance(np.ravel(total), "MM").value("IN")
    nc.close()
    df.to_file("combined.shp")


if __name__ == "__main__":
    main()
