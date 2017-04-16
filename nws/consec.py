"""Do Something Fun"""
import psycopg2
from pandas.io.sql import read_sql


def main():
    """Do Something"""
    pgconn = psycopg2.connect(database='postgis', host='localhost',
                              port=5555, user='nobody')
    df = read_sql("""SELECT ugc, eventid,
    generate_series(issue, expire, '1 minute'::interval) as ts from warnings
    WHERE phenomena = 'TO' and significance = 'W'
    ORDER by ts ASC
    """, pgconn, index_col=None)
    maxrunning = 0
    for ugc, gdf in df.groupby('ugc'):
        lastts = gdf.iloc[0]['ts']
        running = [0, lastts, None]
        for _, row in gdf.iterrows():
            delta = (row['ts'] - lastts).total_seconds()
            if delta > 61:
                running = [0, row['ts'], None]
            else:
                if (row['ts'] - running[1]).total_seconds() > maxrunning:
                    print ugc, maxrunning / 3600., row['ts'], running[1]
                    maxrunning = (row['ts'] - running[1]).total_seconds()
            lastts = row['ts']


if __name__ == '__main__':
    main()
