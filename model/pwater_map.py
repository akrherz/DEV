"""Map of precipitable water"""
from __future__ import print_function
import psycopg2
import numpy as np
from pandas.io.sql import read_sql
from pyiem.datatypes import distance
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
import matplotlib.pyplot as plt


def main():
    """Go Main"""
    nt = NetworkTable(['AWOS', 'IA_ASOS'])
    pgconn = psycopg2.connect(database='mos', host='localhost', user='nobody',
                              port=5555)
    df = read_sql("""
    select station, avg(pwater) from model_gridpoint where
    model = 'NAM' and extract(hour from runtime at time zone 'UTC') = 0
    and pwater > 0 and pwater < 100 and
    extract(month from runtime) between 4 and 9 and ftime = runtime
    GROUP by station ORDER by avg
    """, pgconn, index_col='station')
    df['lat'] = None
    df['lon'] = None
    df['pwater'] = distance(df['avg'].values, 'MM').value('IN')
    for station in df.index.values:
        df.at[station, 'lat'] = nt.sts[station[1:]]['lat']
        df.at[station, 'lon'] = nt.sts[station[1:]]['lon']

    mp = MapPlot(title=('00z Analysis NAM Warm-Season Average '
                        'Precipitable Water [in]'),
                 subtitle=("based on grid point samples "
                           "from 2004-2017 (April-September)"))
    cmap = plt.get_cmap("plasma_r")
    cmap.set_under('white')
    cmap.set_over('black')
    mp.contourf(df['lon'], df['lat'], df['pwater'],
                np.arange(0.94, 1.13, 0.03), cmap=cmap,
                units='inch')
    mp.drawcounties()
    mp.drawcities()
    mp.postprocess(filename='170901.png')
    mp.close()


if __name__ == '__main__':
    main()
