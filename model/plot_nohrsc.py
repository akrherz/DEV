"""Plot WPC"""
from __future__ import print_function
import glob

import numpy as np
import netCDF4
from metpy.units import units
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem import reference


def main():
    """Go Main"""
    nc = netCDF4.Dataset('sfav2_CONUS_2018093012_to_2018121012.nc')
    lats = nc.variables['lat'][:]
    lons = nc.variables['lon'][:]
    data = nc.variables['Data'][:] * 1000. / 25.4
    nc.close()

    mp = MapPlot(
        sector='iowa', continentalcolor='tan',
        title=("National Snowfall Analysis - NOHRSC "
               "- Season Total Snowfall"),
        subtitle='Snowfall up until 7 AM 10 Dec 2018')
    cmap = plt.get_cmap('terrain_r')
    levs = [0.1, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36]
    mp.pcolormesh(lons, lats, data,
                  levs, cmap=cmap, units='inch', clip_on=False)
    mp.drawcounties()
    mp.drawcities()
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
