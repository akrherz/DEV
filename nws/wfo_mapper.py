"""Generic plotter"""
from __future__ import print_function
import datetime
from calendar import month_abbr

import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, drct2text


def get_database_data():
    """Get data from database"""
    pgconn = get_dbconn('postgis')
    df = read_sql("""
    with data as (
        select distinct wfo,
        generate_series(issue, expire, '1 minute'::interval) as ts
        from warnings_2018 where phenomena = 'FL' and significance = 'W')
    select wfo, count(*) / 391621. * 100. as percent from data
    GROUP by wfo ORDER by percent DESC
    """, pgconn, index_col='wfo')
    return df


def main():
    """Go Main"""
    df = get_database_data()
    print(df)
    vals = {}
    labels = {}
    for wfo, row in df.iterrows():
        if wfo == 'JSJ':
            wfo = 'SJU'
        vals[wfo] = row['percent']
        labels[wfo] = '%.0f%%' % (row['percent'], )
        #if row['count'] == 0:
        #    labels[wfo] = '-'

    bins = np.arange(0, 101, 10)    
    #bins = [1, 25, 50, 75, 100, 125, 150, 200, 300]
    #bins = [-50, -25, -10, -5, 0, 5, 10, 25, 50]
    # bins[0] = 1
    #clevlabels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    cmap = plt.get_cmap('PuOr')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("2018 Percentage of Time with 1+ Flood Warning Active"),
                 subtitle=('1 January - 30 September 2018, based on IEM archives'))
    mp.fill_cwas(vals, bins=bins, lblformat='%s', labels=labels,
                 cmap=cmap, ilabel=True,  # clevlabels=clevlabels,
                 units='percent')
    
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
