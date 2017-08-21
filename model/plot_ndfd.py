"""Plot WPC"""
from __future__ import print_function
import datetime
import subprocess

import pygrib
from pyiem.plot import MapPlot
import numpy as np
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs

WANT = datetime.datetime(2017, 8, 21, 18)  # UTC


def main():
    """Go Main"""
    msgnumber = None
    subprocess.call(("wget -O ds.sky.bin ftp://tgftp.nws.noaa.gov/"
                     "SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/"
                     "VP.001-003/ds.sky.bin"
                     ), shell=True)
    grbs = pygrib.open('ds.sky.bin')
    for grb in grbs:
        if grb.validDate == WANT:
            msgnumber = grb.messagenumber

    print("Message number is %s" % (msgnumber, ))
    grb = grbs[msgnumber]
    analtime = grb.analDate - datetime.timedelta(hours=5)
    lats, lons = grb.latlons()

    for sector in ['conus', 'midwest']:
        mp = MapPlot(sector=sector,
                     axisbg='tan',
                     title=("NWS Forecasted Sky Cover [%] "
                            "for 1 PM CDT 21 August 2017"),
                     subtitle=('NDFD Forecast issued %s, Red '
                               'swath is path of eclipse totality'
                               ) % (analtime.strftime("%-I %p %-d %B %Y")))

        mp.pcolormesh(lons, lats, grb['values'],
                      np.arange(0, 101, 25.), cmap=plt.get_cmap('binary_r'),
                      units='Sky Coverage %')

        shp = shpreader.Reader('upath17.shp')
        mp.ax.add_geometries(shp.geometries(), ccrs.PlateCarree(),
                             facecolor='None', edgecolor='r', zorder=100)

        mp.postprocess(filename='test.png')
        mp.close()
        subprocess.call(("scp test.png mesonet@mesonet:/mesonet/share/pickup/"
                         "eclipse_%s.png") % (sector, ), shell=True)


if __name__ == '__main__':
    main()
