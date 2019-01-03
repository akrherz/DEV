"""Dump daily precip totals to shapefiles.

NOTE: DBF has a 256 column limit, so we dump twice here.
"""
from __future__ import print_function
import datetime

from shapely.geometry import Point
import geopandas as gpd
import numpy as np
import netCDF4
from pyiem import util
from pyiem import iemre
from pyiem import reference
from pyiem.datatypes import distance


def compute_bounds(nc):
    """Figure out what is needed for a grid bounds for stage IV"""
    lats = nc.variables['lat'][:]
    lons = nc.variables['lon'][:]
    for lon, lat in [[reference.MW_WEST, reference.MW_NORTH],
                     [reference.MW_WEST, reference.MW_SOUTH],
                     [reference.MW_EAST, reference.MW_NORTH],
                     [reference.MW_EAST, reference.MW_SOUTH]]:
        dist = ((lons - lon)**2 + (lats - lat)**2)**0.5
        print(np.unravel_index(dist.argmin(), dist.shape))


def main():
    """Go Main Go"""
    nc = netCDF4.Dataset('/mesonet/data/stage4/2018_stage4_hourly.nc')
    precip = nc.variables['p01m']
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
    lats = nc.variables['lat'][south:north, west:east]
    lons = nc.variables['lon'][south:north, west:east]
    pts = []
    for lon, lat in zip(np.ravel(lons), np.ravel(lats)):
        pts.append(Point(lon, lat))
    df = gpd.GeoDataFrame({'geometry': pts})
    # iterate over days
    now = datetime.date(2018, 7, 1)
    ets = datetime.date(2019, 1, 1)
    while now < ets:
        valid = util.utc(now.year, now.month, now.day, 5)
        tidx0 = iemre.hourly_offset(valid)
        now += datetime.timedelta(days=1)
        valid = util.utc(now.year, now.month, now.day, 5)
        tidx1 = iemre.hourly_offset(valid)
        data = precip[tidx0:tidx1, south:north, west:east]
        total = np.sum(data, axis=0)
        print("Processing %s max precip: %.2f" % (
            now - datetime.timedelta(days=1), np.max(total)))
        df[(now - datetime.timedelta(days=1)).strftime("%b%d")
           ] = distance(np.ravel(total), 'MM').value("IN")
    df.to_file('combined.shp')


if __name__ == '__main__':
    main()
