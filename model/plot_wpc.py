"""Plot WPC"""
from __future__ import print_function

import pygrib
from pyiem.plot import MapPlot
from pyiem import reference
from pyiem.datatypes import distance
import numpy as np


def main():
    """Go Main"""
    g = pygrib.open('/tmp/p120m_2017062700f120.grb')

    grb = g[1]
    lats, lons = grb.latlons()

    mp = MapPlot(sector='custom', project='aea',
                 south=reference.MW_SOUTH, north=reference.MW_NORTH,
                 east=reference.MW_EAST, west=reference.MW_WEST,
                 axisbg='tan',
                 title=("Weather Prediction Center (WPC) "
                        "5 Day Forecasted Precipitation"),
                 subtitle='7 PM 26 June thru 7 PM 1 July 2017')

    mp.contourf(lons, lats, distance(grb['values'], 'MM').value('IN'),
                np.arange(0, 4.6, 0.5), units='inches')

    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
