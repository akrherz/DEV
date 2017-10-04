"""Generic plotter"""
from __future__ import print_function
import datetime

import numpy as np
from pyiem.plot import MapPlot
from pyiem.network import Table
import matplotlib.pyplot as plt
import psycopg2
from pandas.io.sql import read_sql


def get_database_data():
    """Get data from database"""
    pgconn = psycopg2.connect(database='postgis', host='localhost',
                              port=5555, user='nobody')
    df = read_sql("""
    with bnds as (
        select wfo, min(extract(year from issue)) from sbw
        WHERE phenomena = 'FL' and significance = 'W'
        and issue > '2001-01-01' GROUP by wfo)
    select s.wfo, b.min::int as year from sbw s, bnds b
    WHERE s.wfo = b.wfo ORDER by year ASC
    """, pgconn, index_col='wfo')
    print(df['year'].describe())
    return df['year'].to_dict()


def main():
    """Go MAin"""
    vals = get_database_data()

    bins = np.arange(2011, 2019, 1, dtype='i')
    cmap = plt.get_cmap('plasma')
    cmap.set_over('black')
    cmap.set_under('black')
    mp = MapPlot(sector='nws', continentalcolor='white',
                 title=("Year of First Flood Warning (FL.W) Polygon"),
                 subtitle=('based on unofficial IEM Processing and Archiving'))
    mp.fill_cwas(vals, bins=bins, lblformat='%.0f', cmap=cmap, ilabel=True,
                 units='Count')
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
