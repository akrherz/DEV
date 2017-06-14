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
    with bnds as (
        select wfo, min(issue) from sbw where phenomena = 'SV'
        and hailtag > 0 GROUP by wfo)
    select s.wfo, sum(case when tornadotag = 'POSSIBLE' then 1 else 0 end)
    / count(*)::float * 100. as val from sbw s, bnds b
    WHERE s.wfo = b.wfo and s.expire >= b.min and
    s.status != 'NEW'
    and s.phenomena = 'SV' GROUP by s.wfo ORDER by val
    """, pgconn, index_col='wfo')
    return df['val'].to_dict()


def main():
    """Go MAin"""
    vals = get_database_data()

    bins = np.arange(0, 41.0, 4.0)
    cmap = plt.get_cmap('plasma')
    mp = MapPlot(sector='nws', continental_color='white',
                 title=("2010-17 % of SVR Warn SVS Update "
                        "with TORNADO POSSIBLE Tag"),
                 subtitle=('based on unofficial IEM Data and for period of '
                           'tag issuance per office, SVSs not weighted by warning'))
    mp.fill_cwas(vals, bins=bins, lblformat='%.1f', cmap=cmap, ilabel=True,
                 units='Count')
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
