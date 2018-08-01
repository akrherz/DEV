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
    WITH data as (
        select wfo, extract(year from issue) as year, count(*) from sbw
        WHERE extract(month from issue) = 7 and status = 'NEW' and
        phenomena in ('TO', 'SV') and significance = 'W'
        and issue > '2008-01-01' GROUP by wfo, year
    ), agg as (
        select wfo, sum(count) / 10. as avg
        from data where year < 2018 GROUP by wfo
    ), d2018 as (
        select wfo, count from data where year = 2018
    )
    select a.wfo, a.avg, d.count from
    agg a LEFT JOIN d2018 d on (a.wfo = d.wfo)
    """, pgconn, index_col=None)
    return df


def main():
    """Go Main"""
    df = get_database_data()
    df.fillna(0, inplace=True)
    df['diff'] = df['count'] - df['avg']
    df['percent'] = df['count'] / df['avg'] * 100.
    df.set_index('wfo', inplace=True)
    print(df)
    vals = {}
    labels = {}
    for wfo, row in df.iterrows():
        if wfo == 'JSJ':
            wfo = 'SJU'
        vals[wfo] = row['diff']
        labels[wfo] = '%.1f' % (row['diff'], )
        #if row['count'] == 0:
        #    labels[wfo] = '-'
        
    #bins = [1, 25, 50, 75, 100, 125, 150, 200, 300]
    bins = [-50, -25, -10, -5, 0, 5, 10, 25, 50]
    # bins[0] = 1
    #clevlabels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    cmap = plt.get_cmap('PuOr')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("July 2018 Severe T'Storm + Tornado Warning Count Departure from Average"),
                 subtitle=('2018 count minus 2008-2017 average warning count, based on IEM archives, CDT Period'))
    mp.fill_cwas(vals, bins=bins, lblformat='%.0f', labels=labels,
                 cmap=cmap, ilabel=True,  # clevlabels=clevlabels,
                 units='count difference')
    
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
