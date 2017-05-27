"""Generic plotter"""
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
    with data as (
        select wfo, eventid, extract(year from expire) as yr, count(*)
        from sbw where expire > '2012-01-01' and phenomena = 'SV'
        and significance = 'W' GROUP by wfo, eventid, yr)

    select wfo, avg(count) - 1 as val from data GROUP by wfo ORDER by val DESC
    """, pgconn, index_col='wfo')
    return df['val'].to_dict()


def main():
    """Go MAin"""
    vals = get_database_data()

    bins = np.arange(0, 4.3, 0.25)
    cmap = plt.get_cmap('plasma')
    p = MapPlot(sector='nws', continental_color='white',
                title="2012-17 Average Number of SVS Updates per SVR T'Storm Warning",
                subtitle='based on unofficial IEM Data')
    p.fill_cwas(vals, bins=bins, lblformat='%.1f', cmap=cmap, ilabel=True,
                units='Count')
    p.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
