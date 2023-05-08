"""Dump daily precip totals to shapefiles.

NOTE: DBF has a 256 column limit, so we dump twice here.
"""

import netCDF4
import numpy as np

import geopandas as gpd
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
    nc = netCDF4.Dataset("/mesonet/data/iemre/2021_iemre_hourly.nc")
    nc.variables["tmpk"]
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
    for lon, lat in zip(np.ravel(lons), np.ravel(lats)):
        pts.append(Point(lon, lat))
    df = gpd.GeoDataFrame({"geometry": pts})
    for year in range(1997, 2022):
        nc = netCDF4.Dataset(f"/mesonet/data/iemre/{year}_iemre_hourly.nc")
        tmpk = nc.variables["tmpk"]
        tidx0 = iemre.hourly_offset(util.utc(year, 6, 1, 5))
        tidx1 = iemre.hourly_offset(util.utc(year, 9, 1, 5))
        data = np.mean(tmpk[tidx0:tidx1:24, south:north, west:east], axis=0)
        df[f"m{year}f"] = util.c2f(np.ravel(data) - 273.15)
        data = np.mean(
            tmpk[tidx0 + 12 : tidx1 + 12 : 24, south:north, west:east], axis=0
        )
        df[f"n{year}f"] = util.c2f(np.ravel(data) - 273.15)
        nc.close()
    df.to_file("temps.shp")


if __name__ == "__main__":
    main()
