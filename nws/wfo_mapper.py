"""Generic plotter"""
from __future__ import print_function
import datetime

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
        select distinct wfo, valid, geom from lsrs_2018 WHERE
        valid >= '2018-04-01' and type = 'S'
        )
    select wfo, count(*) from data GROUP by wfo ORDER by count DESC
    """, pgconn, index_col='wfo')
    print(df['count'].describe())
    return df['count'].to_dict()


def main():
    """Go MAin"""
    vals = get_database_data()

    bins = np.arange(0, 900, 100, dtype='i')
    bins[0] = 1
    cmap = plt.get_cmap('plasma')
    cmap.set_over('black')
    cmap.set_under('white')
    mp = MapPlot(sector='nws', continentalcolor='white',
                 title=("April 2018 Number of Local Storm Reports for Snowfall Issued"),
                 subtitle=('based on unofficial IEM Processing thru 18 April 2018 18 UTC (number of reports not LSR Text Products)'))
    mp.fill_cwas(vals, bins=bins, lblformat='%.0f', cmap=cmap, ilabel=True,
                 units='Count')
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
