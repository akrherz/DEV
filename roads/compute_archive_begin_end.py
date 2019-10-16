"""Figure out what our time domain is for our segments."""

from pyiem.util import get_dbconn
import pandas as pd
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    pgconn = get_dbconn('postgis')
    base = read_sql("""
    select segid, archive_begin, archive_end from roads_base
    """, pgconn, index_col='segid')
    for year in range(2003, 2018):
        table = "roads_%s_%s_log" % (year, year + 1)
        df = read_sql("""
            SELECT segid, min(valid), max(valid) from """ + table + """
            WHERE valid is not null GROUP by segid
        """, pgconn, index_col='segid')
        for segid, row in df.iterrows():
            curmin = base.at[segid, 'archive_begin']
            curmax = base.at[segid, 'archive_end']
            if curmin is None or row['min'] < curmin:
                base.at[segid, 'archive_begin'] = row['min']
            if curmax is None or row['max'] > curmax:
                base.at[segid, 'archive_end'] = row['max']

    cursor = pgconn.cursor()
    for segid, row in base.iterrows():
        if pd.isnull(row['archive_begin']) or pd.isnull(row['archive_end']):
            continue
        print("%s %s -> %s" % (
            segid, row['archive_begin'], row['archive_end']))
        cursor.execute("""
        update roads_base SET archive_begin = %s, archive_end = %s
        where segid = %s
        """, (row['archive_begin'], row['archive_end'], segid))
    cursor.close()
    pgconn.commit()


if __name__ == '__main__':
    main()
