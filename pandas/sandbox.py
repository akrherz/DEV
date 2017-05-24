import psycopg2
from pandas.io.sql import read_sql
import pandas as pd
import calendar
import datetime
import pytz
import numpy as np
from geopandas import GeoDataFrame
from rasterio import features
from pyiem import reference
import requests

basets = datetime.datetime(2016, 11, 17).replace(tzinfo=pytz.utc)
x = [basets + datetime.timedelta(seconds=i/20.) for i in range(10000)]

df = pd.DataFrame({'valid': x})

#df['delta'] = (df['valid'] - basets) / np.timedelta64(1, 's')
#df['sample'] = ((df['delta'] * 100) - (df['delta'].astype('i') * 100)) / 5

for i, row in df.iterrows():
    delta = (row['valid'] - basets).total_seconds()
    tm = int(delta)
    sample = int((delta * 100) - (tm * 100)) / 5

#print df
