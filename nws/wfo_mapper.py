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


def get_database_data(phenomena):
    """Get data from database"""
    pgconn = get_dbconn('postgis')
    df = read_sql("""
    WITH data as (
        SELECT wfo, tml_direction / 5 * 5 as drct, count(*) from sbw
        WHERE phenomena = %s and status = 'NEW' and significance = 'W'
        and tml_direction >= 0 and tml_direction <= 360
        GROUP by wfo, drct),
    agg as (
        SELECT wfo, drct,
        rank() OVER (PARTITION by wfo ORDER by count DESC, drct ASC)
        from data
    )
    select wfo, drct from agg where rank = 1
    """, pgconn, params=(phenomena, ), index_col='wfo')
    return df


def draw_line(plt, x, y, angle):
    """Draw a line"""
    r = 0.25
    plt.arrow(x, y, r * np.cos(angle), r * np.sin(angle),
              head_width=0.35, head_length=0.5, fc='k', ec='k')


def main():
    """Go Main"""
    nt = NetworkTable("WFO")
    todf = get_database_data("TO")
    todf['drct2'] = (270. - todf['drct']) / 180. * np.pi
    svdf = get_database_data("SV")
    svdf['drct2'] = (270. - svdf['drct']) / 180. * np.pi
    vals = {}
    labels = {}
    for wfo, row in svdf.iterrows():
        if wfo not in todf.index.values:
            continue
        diff = todf.at[wfo, 'drct'] - row['drct'] 
        if diff > 180:
            diff = diff - 180
        if diff < -180:
            diff = diff + 180
        if wfo == 'JSJ':
            wfo = 'SJU'
        vals[wfo] = diff
        labels[wfo.encode('utf-8')] = drct2text(row['drct'])
        
    bins = range(-180, 181, 45)
    #clevlabels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    cmap = plt.get_cmap('RdBu')
    #cmap.set_over('black')
    #cmap.set_under('white')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("2007-2018 Difference in Most Frequent Storm Motion (SVR to TOR)"),
                 subtitle=('based on IEM archives of issuance Time...Motion...Location warning tags, binned every 5 degrees, (+) val is clockwise'))
    mp.fill_cwas(vals, bins=bins, lblformat='%.0f',  # labels=labels,
                 cmap=cmap, ilabel=True, #  clevlabels=clevlabels,
                 units='Direction Difference ($^\circ$)')
    
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
