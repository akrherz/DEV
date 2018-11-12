"""Dot provided me an archive, so I better ingest it!"""

import geopandas as gpd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn('postgis')
    codes = read_sql("""
    SELECT segid, idot_id, major || ': ' || minor as label from roads_base
    WHERE archive_end is null or archive_end > '2017-01-01'
    """, pgconn, index_col=None)
    df = gpd.read_file('Export20162017.shp')
    # HEADLINE should be mapable back to my cond
    # DATE_UTC
    # CARS_SEGMENT_ID ?
    # CARS_SHORT_NAME
    unknown = []
    for _i, row in df.iterrows():
        if row['CARS_SEGME'] not in codes['idot_id'].values:
            if row['CARS_SEGME'] not in unknown:
                print(row)
                unknown.append(row['CARS_SEGME'])
    print(len(unknown))


if __name__ == '__main__':
    main()
