"""Plot WPC"""
from __future__ import print_function
import glob

import pygrib
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pyiem.plot import MapPlot
from pyiem import reference
from pyiem.datatypes import distance


def main():
    """Go Main"""
    total = None
    for fn in glob.glob("/tmp/psnow72_ge4_2018032200f072.grb"):
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
                        "Probability of 4+ Inches of Snowfall"),
                 subtitle='Falling between 7 PM 21 March and 7 PM 24 March 2018')
    cmap = plt.get_cmap('viridis')
    cmap.set_bad('tan')
    cmap.set_under('white')
    cmap.set_over('red')
    levs = np.arange(0, 101, 20)
    levs[0] = 1
    mp.contourf(lons, lats, total * 100.,
                levs, cmap=cmap, units='percent')

    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
