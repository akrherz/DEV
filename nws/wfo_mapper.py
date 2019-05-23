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
        select wfo, count(*) / 10. as cnt
        from sbw WHERE phenomena in ('TO') and significance = 'W'
        and status = 'NEW' and issue > '2009-01-01' and issue < '2019-01-01'
        and to_char(issue, 'mmdd') < '0523'
        GROUP by wfo),
    d2019 as (
        select wfo, count(*)
        from sbw_2019 WHERE phenomena in ('TO') and significance = 'W'
        and status = 'NEW'
        GROUP by wfo)

    SELECT d.wfo, coalesce(t.count, 0) / d.cnt * 100. as percent from
    data d LEFT JOIN d2019 t on (d.wfo = t.wfo)
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

    # bins = np.arange(0, 101, 10)    
    bins = [1, 25, 50, 75, 100, 125, 150, 200, 300]
    # bins = [-50, -25, -10, -5, 0, 5, 10, 25, 50]
    # bins[0] = 1
    # clevlabels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    cmap = plt.get_cmap('PuOr')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("2019 YTD Issued Tornado Warnings Departure from Average"),
                 subtitle=('1 Jan till 12 AM 23 May 2019 vs 2009-2018, based on IEM archives'))
    mp.fill_cwas(vals, bins=bins, lblformat='%s', labels=labels,
                 cmap=cmap, ilabel=True,  # clevlabels=clevlabels,
                 units='percent')
    
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
