"""Report on our second tipping bucket"""
from __future__ import print_function

import psycopg2
import pandas as pd
from pandas.io.sql import read_sql


def main():
    """Go Main Go"""
    pgconn = psycopg2.connect(database='iem', host='localhost', port=5555,
                              user='nobody')
    amsi4 = read_sql("""
    SELECT to_char(day + '16 hours'::interval, 'YYYY-MM-DD HH:MI AM') as valid,
    pday as coop
    from summary s JOIN stations t on (s.iemid = t.iemid)
    where t.id = 'AMSI4' and day > '2017-07-25' and pday >= 0
    ORDER by day ASC
    """, pgconn, index_col='valid')

    pgconn = psycopg2.connect(database='isuag', host='localhost', port=5555,
                              user='nobody')
    df = read_sql("""
    SELECT to_char(valid, 'YYYY-MM-DD HH:MI AM') as valid,
    rain_mm_tot / 25.4 as bucket1,
    rain_mm_2_tot / 25.4 as bucket2 from sm_hourly where station = 'BOOI4'
    and valid > '2017-07-25' and (rain_mm_tot > 0 or rain_mm_2_tot > 0)
    ORDER by valid ASC
    """, pgconn, index_col='valid')
    df2 = amsi4.join(df, how='outer')
    writer = pd.ExcelWriter('ames_buckets.xlsx')
    df2.to_excel(writer, 'Comparison', index=True)
    writer.save()


if __name__ == '__main__':
    main()
