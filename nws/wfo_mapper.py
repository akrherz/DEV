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
    pgconn = get_dbconn('afos')
    df = read_sql("""
    with data as (
        select source, count(*) from products WHERE
        entered > '2015-01-01' and substr(pil, 1, 3) = 'SPS'
        GROUP by source)

    SELECT substr(source, 2, 3) as wfo, count from data
    ORDER by count DESC
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
        vals[wfo] = row['count']
        labels[wfo] = "{:,}".format(row['count'])

    bins = range(0, 6500, 500)
    bins[0] = 1
    cmap = plt.get_cmap('plasma_r')
    cmap.set_over('black')
    cmap.set_under('white')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("1 Jan 2015 - 24 Apr 2018 Number of Special Weather Statements (SPS) Issued"),
                 subtitle=('based on unofficial IEM Archives'))
    mp.fill_cwas(vals, bins=bins, lblformat='%s', labels=labels,
                 cmap=cmap, ilabel=True, # clevlabels=month_abbr[1:],
                 units='Count')
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
