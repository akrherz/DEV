"""Where are the CWA borders at?"""
from __future__ import print_function

import matplotlib
matplotlib.use('agg')
import numpy as np
import matplotlib.pyplot as plt
from pandas.io.sql import read_sql
from tqdm import tqdm
from pyiem.util import get_dbconn
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable


def main():
    """Go Main Go"""
    pgconn = get_dbconn('postgis', user='nobody')
    df = read_sql("""
    SELECT st_x(geom::geometry) as lon, st_y(geom::geometry) as lat
    from pireps where st_x(geom::geometry) between -130 and -50
    and st_y(geom::geometry) between 10 and 52
    """, pgconn, index_col=None)
    h2d, xedges, yedges = np.histogram2d(df['lon'], df['lat'], 100)
    print(np.max(h2d))

    cmap = plt.get_cmap('Reds')
    cmap.set_under('white')
    cmap.set_over('black')
    ramp = np.arange(0, 1001, 100)
    ramp[0] = 1
    mp = MapPlot(sector='conus', continentalcolor='tan',
                 title='20 Jan 2015 - 28 Jan 2018 NWS All PIREPs Heatmap',
                 subtitle=('Based on IEM Processing, %.0f PIREPs plotted'
                           ) % (len(df.index), ))
    mp.pcolormesh(xedges, yedges, h2d.T, ramp, clip_on=False,
                  cmap=cmap, units='count')
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
