"""Generic plotter"""
from __future__ import print_function
import datetime
from calendar import month_abbr

import numpy as np
from pandas.io.sql import read_sql
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, drct2text


def get_database_data():
    """Get data from database"""
    pgconn = get_dbconn('postgis')
    df = read_sql("""
        SELECT wfo, sum(case when tml_direction > 180 and tml_direction < 360
        then 1 else 0 end) / count(*)::float * 100. as percent from sbw
        WHERE phenomena = 'SV' and status = 'NEW' and significance = 'W'
        and tml_direction >= 0 and tml_direction <= 360
        GROUP by wfo
    """, pgconn, index_col='wfo')
    return df


def main():
    """Go Main"""
    df = get_database_data()
    vals = {}
    labels = {}
    for wfo, row in df.iterrows():
        if wfo == 'JSJ':
            wfo = 'SJU'
        vals[wfo] = row['percent']
        labels[wfo.encode('utf-8')] = ''
        
    bins = list(range(0, 101, 10))
    bins[0] = 1
    #clevlabels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    cmap = plt.get_cmap('plasma')
    cmap.set_over('black')
    cmap.set_under('white')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("2007-2018 Percent of Severe T'Storm Warnings with Storm Motion > 180$^\circ$ and < 360$^\circ$"),
                 subtitle=('based on IEM archives of issuance Time...Motion...Location warning tags, storm motion west to east'))
    mp.fill_cwas(vals, bins=bins, lblformat='%.0f',  # labels=labels,
                 cmap=cmap, ilabel=True, #  clevlabels=clevlabels,
                 units='percent')
    
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
