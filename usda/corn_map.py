"""Make a map"""
from __future__ import print_function

import matplotlib.pyplot as plt
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_dbconn
import pandas as pd
from pandas.io.sql import read_sql


def get_data():
    """The data we want and the data we need"""
    pgconn = get_dbconn('coop', user='nobody')
    df = read_sql("""
        select year, week_ending, num_value, state_alpha from nass_quickstats
        where commodity_desc = 'CORN' and statisticcat_desc = 'PROGRESS'
        and unit_desc = 'PCT HARVESTED' and
        util_practice_desc = 'GRAIN' and num_value is not null
        ORDER by state_alpha, week_ending
    """, pgconn, index_col=None)
    df['week_ending'] = pd.to_datetime(df['week_ending'])
    data = {}
    for state, gdf in df.groupby('state_alpha'):
        sdf = gdf.copy()
        sdf.set_index('week_ending', inplace=True)
        newdf = sdf.resample('D').interpolate(method='linear')
        y10 = newdf[newdf['year'] > 2006]
        doyavgs = y10.groupby(y10.index.strftime("%m%d")).mean()
        lastdate = pd.Timestamp(newdf.index.values[-1]).to_pydatetime()
        data[state] = {'date': lastdate,
                       'avg': doyavgs.at[lastdate.strftime("%m%d"),
                                         'num_value'],
                       'd2017': newdf.at[lastdate,
                                         'num_value']}
        print("%s %s" % (state, data[state]))
    return data


def main():
    """Go Main Go"""
    data = get_data()
    mp = MapPlot(sector='midwest',
                 title='5 Nov 2017 USDA NASS Corn Grain Harvest Completion',
                 subtitle=('Top value is 2017 completion, bottom value is '
                           'departure from 2007-2016 avg'))
    data2 = {}
    labels = {}
    for state in data:
        val = data[state]['d2017'] - data[state]['avg']
        data2[state] = data[state]['d2017']
        labels[state] = "%.0f%%\n%.1f%%" % (data[state]['d2017'],
                                            val)

    mp.fill_states(data2, ilabel=True, labels=labels,
                   cmap=plt.get_cmap('terrain'), units='%')
    mp.postprocess(filename='test.png')
    mp.close()


if __name__ == '__main__':
    main()
