import psycopg2
from pandas.io.sql import read_sql
import pandas as pd
import calendar
import datetime
import numpy as np
from geopandas import GeoDataFrame
from rasterio import features
from pyiem import reference

pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

station = 'IA2203'
table = 'alldata_ia'
df = read_sql("""
    WITH avgs as (
        SELECT sday, avg(gddxx(50, 86, high, low)) as cgdd,
        avg(sdd86(high, low)) as csdd86, avg(precip) as cprecip
        from """+table+"""
        WHERE station = %s GROUP by sday
    )
    SELECT day, gddxx(50, 86, high, low) as gdd, cgdd from """+table+""" d
    JOIN avgs a on (d.sday = a.sday)
    WHERE station = %s and d.sday != '0229' ORDER by day ASC
    """, pgconn, params=(station, station), index_col='day')

df['cgdd_diff'] = df['gdd'] - df['cgdd']

arr = np.ma.zeros((2017-1893, 366))
arr[:] = np.nan

for yr in range(1893, 2017):
  sts = datetime.date(yr, 10, 3)
  ets = datetime.date(yr+1, 2, 18)

  vals = df.loc[sts:ets, 'cgdd_diff'].cumsum().values
  arr[yr-1893,:len(vals)] = vals

print np.nanmax(arr, 0)
