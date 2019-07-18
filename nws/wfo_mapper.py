"""Generic plotter"""
from __future__ import print_function
import datetime
from calendar import month_abbr

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from tqdm import tqdm
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, drct2text


def get_database_data():
    """Get data from database"""
    return pd.read_csv('data.csv', index_col='wfo')
    data = {'wfo': [], 'days': []}
    nt = NetworkTable("WFO")
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()
    for sid in tqdm(nt.sts):
        cursor.execute("""
            select distinct date(expire - '1 day'::interval)
            from spc_outlooks o, ugcs c where day = 1 and threshold = 'MDT'
            and ST_Intersects(c.geom, o.geom) and c.wfo = %s
            and c.end_ts is null
        """, (sid, ))
        data['wfo'].append(sid)
        data['days'].append(cursor.rowcount)

    df = pd.DataFrame(data)
    df.to_csv('data.csv')
    return df


def main():
    """Go Main"""
    df = get_database_data()
    pgconn = get_dbconn('postgis')
    df2 = read_sql("""
        SELECT wfo, st_area(the_geom::geography) / 1000000000. as area
        from cwa""" 
    , pgconn, index_col='wfo')
    df['area'] = df2['area']
    df['ratio'] = df['days'] / df['area']
    print(df['ratio'].describe())
    vals = {}
    labels = {}
    for wfo, row in df.iterrows():
        if wfo == 'JSJ':
            wfo = 'SJU'
        vals[wfo] = row['ratio']
        labels[wfo] = '%.1f' % (row['ratio'], )
        #if row['count'] == 0:
        #    labels[wfo] = '-'

    bins = np.arange(0, 3.1, 0.25)    
    # bins = [1, 2, 5, 10, 20, 30, 50, 75, 100, 125, 150, 175]
    # bins = [-50, -25, -10, -5, 0, 5, 10, 25, 50]
    # bins[0] = 1
    # clevlabels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    cmap = plt.get_cmap('magma')
    mp = MapPlot(sector='conus', continentalcolor='white', figsize=(12., 9.),
                 title=("2002-2019 SPC Day 1 Moderate Convective Risk Days/WFO Area by WFO"),
                 subtitle=('till 17 Jul 2019, based on unofficial IEM Archives of any part of risk area overlapping CWA'))
    mp.fill_cwas(vals, bins=bins, lblformat='%s', labels=labels,
                 cmap=cmap, ilabel=True,  # clevlabels=clevlabels,
                 units='days / 1000 sqkm')
    
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
