"""Deduplicate."""
import sys

from tqdm import tqdm
from pandas.io.sql import read_sql
from pyiem.util import noaaport_text, get_dbconn


def dotable(table):
    """Go main go"""
    pgconn = get_dbconn('afos')
    cursor = pgconn.cursor()
    df = read_sql("""
        WITH data as (
            SELECT entered, pil, wmo, source, count(*) from """ + table + """
            WHERE source is not null and wmo is not null and pil is not null
            and entered is not null GROUP by entered, pil, wmo, source)
        select * from data where count > 1
    """, pgconn, index_col=None)
    hits = 0
    for _, row in tqdm(
            df.iterrows(), total=len(df.index), desc=table, disable=False):
        # get text
        cursor.execute("""
            SELECT data from """ + table + """
            WHERE source = %s and entered = %s and pil = %s and wmo = %s
        """, (row['source'], row['entered'], row['pil'], row['wmo']))
        data = []
        for row2 in cursor:
            data.append(noaaport_text(row2[0]))
        if data[0][11:] == data[1][11:] and len(data) == 2:
            hits += 1
            # delete old entries
            cursor.execute("""
            DELETE from """ + table + """
            WHERE source = %s and entered = %s and pil = %s and wmo = %s
            """, (row['source'], row['entered'], row['pil'], row['wmo']))
            # insert without trailing ^C
            cursor.execute("""
            INSERT into """ + table + """ (data, pil, entered, source, wmo)
            VALUES (%s, %s, %s, %s, %s)
            """, (
                data[0][:-1], row['pil'], row['entered'], row['source'],
                row['wmo'])
            )
        continue
        if data[0][11:] != data[1][11:]:
            o = open('one.txt', 'w')
            o.write(data[0])
            o.close()
            o = open('two.txt', 'w')
            o.write(data[1])
            o.close()
            sys.exit()
    print("%s rows were updated..." % (hits, ))
    cursor.close()
    pgconn.commit()
    pgconn.close()


def main():
    """Do Main"""
    for year in range(1996, 2018):
        for col in ['0106', '0712']:
            table = "products_%s_%s" % (year, col)
            dotable(table)


if __name__ == '__main__':
    main()
