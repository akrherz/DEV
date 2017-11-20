"""Fill a data request from Fawaz Alharbi"""
from __future__ import print_function
from StringIO import StringIO

import geopandas as gpd
import pandas as pd
from pyiem.util import get_dbconn
import requests
import tqdm


def main():
    """Go """
    pgconn = get_dbconn('coop', user='nobody')
    df = gpd.read_postgis("""
    WITH data as (
        SELECT station, year, avg((high+low)/2.) as avg_temp,
        sum(precip) as tot_precip, sum(snow) as tot_snow
        from alldata_ia where year >= 1998 and year < 2016
        and station != 'IA0000' and substr(station, 3, 1) != 'C'
        GROUP by station, year
    ), agg as (
        SELECT station, avg(avg_temp) as avg_temp,
        sum(case when tot_snow = 0 then 1 else 0 end) as snow_missing,
        avg(tot_precip) as tot_precip, avg(tot_snow) as tot_snow
        from data GROUP by station
    )
    select a.*, t.geom from agg a JOIN stations t on (a.station = t.id)
    WHERE t.network = 'IACLIMATE' and snow_missing < 3
    """, pgconn, geom_col='geom', index_col='station')
    df.drop('snow_missing', axis=1, inplace=True)
    df['avg_cycles'] = 0

    for station in tqdm.tqdm(df.index.values):
        uri = ("http://iem.local/plotting/auto/plot/121/network:IACLIMATE::"
               "station:%s::thres1:30-32::dpi:100.csv") % (station, )
        req = requests.get(uri)
        ldf = pd.read_csv(StringIO(req.content), index_col='year')
        ldf['total'] = ldf['30-32f'] + ldf['30-32s']
        avg = ldf.loc[slice(1998, 2015)]['total'].mean()
        df.at[station, 'avg_cycles'] = avg

    df.reset_index(inplace=True)
    df.to_file('iowaclimate.shp')


if __name__ == '__main__':
    main()
