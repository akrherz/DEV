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
    WITH data as (
        SELECT wfo, tml_direction / 5 * 5 as drct, count(*) from sbw
        WHERE phenomena = 'TO' and status = 'NEW' and significance = 'W'
        and tml_direction >= 0 and tml_direction <= 360
        GROUP by wfo, drct),
    agg as (
        SELECT wfo, drct,
        rank() OVER (PARTITION by wfo ORDER by count DESC, drct ASC)
        from data
    )
    select wfo, drct from agg where rank = 1
    """, pgconn, index_col='wfo')
    print(df)
    return df


def draw_line(plt, x, y, angle):
    """Draw a line"""
    r = 0.25
    plt.arrow(x, y, r * np.cos(angle), r * np.sin(angle),
              head_width=0.35, head_length=0.5, fc='k', ec='k')


def main():
    """Go Main"""
    nt = NetworkTable("WFO")
    df = get_database_data()
    df['drct2'] = (270. - df['drct']) / 180. * np.pi
    vals = {}
    labels = {}
    for wfo, row in df.iterrows():
        if wfo == 'JSJ':
            wfo = 'SJU'
        vals[wfo] = row['drct']
        labels[wfo.encode('utf-8')] = drct2text(row['drct'])
        
    bins = range(0, 361, 45)
    clevlabels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    cmap = plt.get_cmap('plasma_r')
    cmap.set_over('black')
    cmap.set_under('white')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("2007-2018 Most Frequent Storm Motion for Tornado Warnings"),
                 subtitle=('based on IEM archives of issuance Time...Motion...Location warning tags, binned every 5 degrees'))
    mp.fill_cwas(vals, bins=bins, lblformat='%.0f',  # labels=labels,
                 cmap=cmap, ilabel=True, clevlabels=clevlabels,
                 units='Direction ($^\circ$N)')
    
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
