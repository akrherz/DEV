"""Do a comparison with what's on SRH"""
from __future__ import print_function
import datetime

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

SRH = "http://www.srh.noaa.gov/ridge2/shapefiles/psql_currenthazards.html"


def main():
    """Go Main Go"""
    print("Report run at %s" % (datetime.datetime.utcnow(), ))
    srhdf = pd.read_html(SRH, header=0)[0]
    srhdf['wfo'] = srhdf['wfo'].str.slice(1, 4)
    iemdf = read_sql("""
    SELECT wfo, phenomena, significance, eventid, count(*) from warnings
    where expire > now()
    GROUP by wfo, phenomena, significance, eventid
    """, get_dbconn('postgis', user='nobody'), index_col=['wfo', 'phenomena',
                                                          'significance',
                                                          'eventid'])
    for idx, g_srhdf in srhdf.groupby(['wfo', 'phenom', 'sig', 'event']):
        if idx not in iemdf.index:
            print("IEM Missing %s" % (repr(idx),))
            continue
        if len(g_srhdf.index) != iemdf.at[idx, 'count']:
            print(("%s Count Mismatch IEM: %s SRH: %s"
                   ) % (repr(idx), iemdf.at[idx, 'count'], len(g_srhdf.index)))
    for idx, _row in iemdf.iterrows():
        (wfo, phenomena, significance, eventid) = idx
        df2 = srhdf[((srhdf['phenom'] == phenomena) &
                     (srhdf['sig'] == significance) &
                     (srhdf['event'] == eventid) &
                     (srhdf['wfo'] == wfo))]
        if df2.empty:
            print("SRH MISSING %s" % (repr(idx), ))


if __name__ == '__main__':
    main()
