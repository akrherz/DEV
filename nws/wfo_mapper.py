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
    with mins as (
        select wfo, extract(year from issue) as year, min(issue)
        from warnings where issue > '2001-01-01' and
        phenomena in ('SV', 'TO') and significance = 'W' GROUP by wfo, year),
    wfos as (
        select distinct wfo from mins),
    series as (
        select wfo, generate_series(2001, 2018, 1) as year, 
        '1980-12-31'::date from wfos),
    agg as (
        select * from mins UNION select * from series),
    agg2 as (
        select wfo, year, max(min) from agg GROUP by wfo, year), agg3 as (
    select wfo, year,
        case when year = 2018 and extract(year from max) = 1980
        then 'TODAY'::date else max end as ts from agg2),
    agg4 as(
        select wfo, ts, year,
        rank() OVER (PARTITION by wfo ORDER by to_char(ts, 'mmdd') DESC, year DESC)
        from agg3)

    select wfo, year, ts, extract(doy from ts) as doy
    from agg4 WHERE rank = 1 ORDER by wfo

    """, pgconn, index_col='wfo')
    return df


def main():
    """Go MAin"""
    df = get_database_data()
    vals = {}
    labels = {}
    for wfo, row in df.iterrows():
        if wfo == 'JSJ':
            wfo = 'SJU'
        if wfo == 'HUN':
            vals[wfo] = 68
            labels[wfo] = "3/9\n2006"
            continue
        if row['ts'].year == 2018 and row['ts'].month == 4 and row['ts'].day == 23:
            vals[wfo] = 400
            labels[wfo] = "2018"
            continue
        if row["ts"].year == 1980:
            vals[wfo] = -1
            labels[wfo] = 'None\n%.0f' % (row['year'], )
            continue
        vals[wfo] = row['doy']
        labels[wfo] = row['ts'].strftime("%-m/%-d\n%Y")

    bins = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365]
    cmap = plt.get_cmap('plasma')
    cmap.set_over('black')
    cmap.set_under('white')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("2001-2018 Latest Date of First WFO Severe T'Storm or Tornado Warning"),
                 subtitle=('based on IEM Archives, Huntsville data to 2003, thru 22 April 2018, 2018 black cells indicate latest date on-going'))
    mp.fill_cwas(vals, bins=bins, lblformat='%s', labels=labels,
                 cmap=cmap, ilabel=True, clevlabels=month_abbr[1:],
                 units='Count')
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
