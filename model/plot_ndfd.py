"""Plot WPC"""
from __future__ import print_function
import datetime
import subprocess

import numpy as np
import pygrib
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot, nwssnow



def main():
    """Go Main"""
    grbs = pygrib.open('ds.snow.bin')
    # skip 1-off first field
    total = None
    lats = lons = None
    for grb in grbs[1:]:
        if lats is None:
            lats, lons = grb.latlons()
            total = grb['values']
            continue
        total += grb['values']
    # TODO tz-hack here
    analtime = grb.analDate - datetime.timedelta(hours=5)

    mp = MapPlot(
        sector='custom', west=-100, east=-92, north=45, south=41,
        axisbg='tan',
        title=("NWS Forecasted Accumulated Snowfall "
               "thru 7 PM 12 April 2019"),
        subtitle='NDFD Forecast Issued %s' % (
            analtime.strftime("%-I %p %-d %B %Y"), )
    )
    cmap = nwssnow()
    cmap.set_bad('tan')
    mp.pcolormesh(
        lons, lats, total * 39.3701,
        [0.01, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36],
        cmap=cmap,
        units='inch')

    mp.drawcounties()
    mp.drawcities()
    mp.postprocess(filename='test.png')
    mp.close()


if __name__ == '__main__':
    main()
