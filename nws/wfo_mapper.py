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
    with warns as (
        SELECT wfo, avg(st_area(geography(geom))) from sbw WHERE
        issue > '2015-01-01' and phenomena = 'SV' and status = 'NEW'
        GROUP by wfo ORDER by wfo
        ),
    sps as (
        SELECT substr(product_id, 15, 3) as wfo, avg(st_area(geography(geom)))
        from text_products where issue > '2015-01-01' GROUP by wfo
    )
    SELECT w.wfo, coalesce(s.avg, 0) / w.avg as ratio
    from warns w LEFT JOIN sps s
    on (w.wfo = s.wfo) ORDER by ratio DESC
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
        vals[wfo] = row['ratio']
        labels[wfo] = "%.1f" % (row['ratio'], )
        
    bins = [0.25, 0.5, 0.75, 1., 1.25, 1.5, 1.75, 2., 5, 10]
    bins[0] = 0.01
    cmap = plt.get_cmap('plasma_r')
    cmap.set_over('black')
    cmap.set_under('white')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("1 Jan 2015 - 24 Apr 2018 Ratio of Average Polygon Size SPS / SVR"),
                 subtitle=('Special Weather Statement (SPS) Polygon to Severe TStorm Polygon, based on unofficial IEM Archives'))
    mp.fill_cwas(vals, bins=bins, lblformat='%s', labels=labels,
                 cmap=cmap, ilabel=True, # clevlabels=month_abbr[1:],
                 units='Ratio')
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
