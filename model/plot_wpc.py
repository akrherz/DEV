"""Plot WPC"""
from __future__ import print_function
import glob

import pygrib
from pyiem.plot import MapPlot
from pyiem import reference
from pyiem.datatypes import distance
import numpy as np


def main():
    """Go Main"""
    total = None
    for fn in glob.glob("/tmp/p24m_201710050*"):
        grbs = pygrib.open(fn)
        grb = grbs[1]
        if total is None:
            total = grb['values']
            lats, lons = grb.latlons()
        else:
            total += grb['values']

    mp = MapPlot(sector='custom', project='aea',
                 south=reference.MW_SOUTH, north=reference.MW_NORTH,
                 east=reference.MW_EAST, west=reference.MW_WEST,
                 axisbg='tan',
                 title=("Weather Prediction Center (WPC) "
                        "3 Day Forecasted Precipitation"),
                 subtitle='7 PM 4 October thru 7 PM 7 October 2017')

    mp.contourf(lons, lats, distance(total, 'MM').value('IN'),
                np.arange(0, 4.6, 0.5), units='inches')

    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
