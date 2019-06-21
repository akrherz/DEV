
import datetime

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def get_data():
    """Go data."""
    pgconn = get_dbconn("coop")
    df = read_sql("""
    with data as (
        select station, year,
        sum(case when high >= 80 then 1 else 0 end) as events from alldata
        WHERE sday < '0620' and year >= 1951
        and substr(station, 3, 1) not in ('C', 'T')
        and substr(station, 3, 4) != '0000' GROUP by station, year),
    climo as (
        select station, sum(events) / count(*) as e from data
        GROUP by station),
    agg as (
        select c.station, c.e, d.events from
        climo c JOIN data d on (c.station = d.station) WHERE d.year = 2019)
    select a.station, st_x(geom) as lon, st_y(geom) as lat,
    a.e as climo_days, a.events as d2019
    from agg a JOIN stations t on (a.station = t.id)
    WHERE t.network ~* 'CLIMATE'
    """, pgconn)
    df.to_csv('data.csv', index=False)


def plot():
    """Go Plot"""
    df = pd.read_csv('data.csv')
    df['diff'] = df['d2019'] - df['climo_days']
    print(df['diff'].describe())

    m = MapPlot(
        sector='conus', axisbg='white',
        title=(
            r'2019 Departure of Days with a High Temperature of 80+$^\circ$F'),
        subtitle=(
            '1 January thru 20 June 2019, based on 1951-2018 climatology of '
            'IEM tracked long term climate sites'))
    cmap = plt.get_cmap('Spectral_r')
    m.contourf(
        df['lon'].values, df['lat'].values, df['diff'].values,
        np.arange(-16, 17, 4), cmap=cmap, units='days')
    m.postprocess(filename='190621.png')
    m.close()


if __name__ == '__main__':
    plot()
