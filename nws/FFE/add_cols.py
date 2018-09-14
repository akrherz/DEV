"""Generic plotter"""
from __future__ import print_function
import datetime
from calendar import month_abbr

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.network import Table
from pyiem.util import get_dbconn


def main():
    """Go MAin"""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()
    df = pd.read_csv('flood_emergencies.csv')
    df2 = df[['source', 'eventid', 'phenomena', 'significance', 'year']
             ].drop_duplicates().copy()
    df2['polygon_area_sqkm'] = None
    for _i, row in df2.iterrows():
        cursor.execute("""
        SELECT ST_area(geom::geography) from sbw WHERE wfo = %s and
        phenomena = %s and significance = %s and eventid = %s and
        extract(year from issue) = %s and status = 'NEW'
        """, (row['source'][1:], row['phenomena'], row['significance'],
              row['eventid'], row['year']))
        res = cursor.fetchone()
        if res is not None:
            df2.at[_i, 'polygon_area_sqkm'] = res[0] / 1e6

    df2.to_csv('flood_emergencies_v2.csv', index=False)


if __name__ == '__main__':
    main()
