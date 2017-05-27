"""Generic plotter"""
import datetime

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
    WITH wfos as (
        SELECT id, tzname from stations where network = 'WFO'),
    data as (
        SELECT wfo, extract(hour from issue at time zone w.tzname) as hr
        from sbw s, wfos w where s.wfo = w.id and
        status = 'NEW' and phenomena = 'TO'
        and significance = 'W')
    select wfo,
    sum(case when hr >= 16 and hr < 21 then 1 else 0 end) /
    count(*)::float * 100. as val from data GROUP by wfo
    """, pgconn, index_col='wfo')
    return df['val'].to_dict()


def main():
    """Go MAin"""
    vals = get_database_data()

    bins = range(0, 101, 10)
    cmap = plt.get_cmap('plasma')
    p = MapPlot(sector='nws', continental_color='white',
                title="2002-17 Percentage of Tornado Warnings between 4 PM and 9 PM",
                subtitle='based on warning issuance using the local time zone of the WFO')
    p.fill_cwas(vals, bins=bins, lblformat='%.0f', cmap=cmap, ilabel=True,
                units='Percentage')
    p.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
