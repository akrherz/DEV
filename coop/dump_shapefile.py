"""Fill a data request from Fawaz Alharbi"""
from __future__ import print_function
from StringIO import StringIO
import shutil

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
        SELECT * from data WHERE tot_snow > 0
    )
    select a.*, t.geom from agg a JOIN stations t on (a.station = t.id)
    WHERE t.network = 'IACLIMATE'
    """, pgconn, geom_col='geom', index_col=None)
    df['cycles'] = 0

    for station in tqdm.tqdm(df['station'].unique()):
        uri = ("http://iem.local/plotting/auto/plot/121/network:IACLIMATE::"
               "station:%s::thres1:30-32::dpi:100.csv") % (station, )
        req = requests.get(uri)
        ldf = pd.read_csv(StringIO(req.content), index_col='year')
        ldf['total'] = ldf['30-32f'] + ldf['30-32s']
        for year in range(1998, 2016):
            val = ldf.loc[year]['total']
            df.loc[((df['year'] == year) &
                    (df['station'] == station)), 'cycles'] = val

    for year in range(1998, 2016):
        df2 = df[df['year'] == year]
        df2.to_file('iowaclimate_%s.shp' % (year, ))
        shutil.copyfile('/mesonet/data/gis/meta/4326.prj',
                        'iowaclimate_%s.prj' % (year, ))


if __name__ == '__main__':
    main()
