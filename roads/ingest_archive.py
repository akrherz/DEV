"""Dot provided me an archive, so I better ingest it!"""

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, utc

LOOKUP = {
 'partially covered with slush': 56,
 'seasonal roadway conditions': 0,
 'completely covered with snow': 47,
 'completely covered with frost': 11,
 'completely covered with slush': 64,
 'partially covered with frost': 3,
 'partially covered with snow': 39,
 'completely covered with ice': 35,
 'impassable': 86,
 'partially covered with ice': 27,
 'travel not advised': 51,
 'partially covered with mixed snow ice or slush': 15,
 'completely covered with mixed snow ice or slush': 23,
}


def main():
    """Go Main Go."""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()
    codes = read_sql("""
    SELECT segid, idot_id, major || ': ' || minor as label from roads_base
    WHERE archive_end > '2018-01-01' and archive_begin < '2018-01-01'
    """, pgconn, index_col='idot_id')

    df = pd.read_csv('1718.csv', sep='|')
    df['idot_id'] = pd.to_numeric(df['CARS_SEGMENT_ID'])
    # HEADLINE should be mapable back to my cond
    # DATE_UTC
    # CARS_SEGMENT_ID ?
    # CARS_SHORT_NAME
    for _i, row in df.iterrows():
        condcode = LOOKUP.get(row['HEADLINE'], 0)  # default to seasonable
        st = str(row['DATE_UTC'])
        tstamp = utc(int(st[:4]), int(st[4:6]), int(st[6:8]), int(st[8:10]),
                     int(st[10:12]), int(st[12:14]))
        cursor.execute("""
            INSERT into roads_2017_2018_log(segid, valid, cond_code, raw)
            VALUES (%s, %s, %s, %s)
        """, (int(codes.at[int(row['idot_id']), 'segid']), tstamp, condcode,
              row['HEADLINE']))
    cursor.close()
    pgconn.commit()


if __name__ == '__main__':
    main()
