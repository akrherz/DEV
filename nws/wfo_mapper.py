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
from pyiem.network import Table
from pyiem.util import get_dbconn


def get_database_data():
    """Get data from database"""
    pgconn = get_dbconn('postgis')
    df = read_sql("""
    with data as (
        select distinct wfo, extract(year from issue) as year,
        extract(week from issue) as week from warnings where
        phenomena in ('TO') and significance  = 'W'
        and issue < '2018-01-01'),
    agg as (
        select wfo, week, count(*) from data GROUP by wfo, week),
    agg2 as (
        select wfo, week, rank() OVER
        (PARTITION by wfo ORDER by count DESC, week ASC)
        from agg)
    select wfo, '2000-01-01'::date + ((week * 7 + 3)::text||' days')::interval
    as date from agg2 where rank = 1 
    """, pgconn, index_col='wfo')
    print(df)
    return df


def main():
    """Go MAin"""
    df = get_database_data()
    vals = {}
    labels = {}
    for wfo, row in df.iterrows():
        if wfo == 'JSJ':
            wfo = 'SJU'
        vals[wfo] = int(row['date'].strftime("%j"))
        labels[wfo] = "%s" % (row['date'].strftime("%b %-d"), )
        
    bins = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    cmap = plt.get_cmap('plasma_r')
    cmap.set_over('black')
    cmap.set_under('white')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("1986-2017 Week with Most Number of Years having 1+ Tornado Warnings"),
                 subtitle=('Midpoint of week plotted, partitioned by week of the year, first week plotted in case of ties, based on unofficial IEM Archives'))
    mp.fill_cwas(vals, bins=bins, lblformat='%s', labels=labels,
                 cmap=cmap, ilabel=True, clevlabels=month_abbr[1:],
                 units='calendar')
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
