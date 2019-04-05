"""Shrug, just do as I am told."""

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

def main():
    """Go Main Go."""
    pgconn = get_dbconn('idep')
    df = read_sql("""
        SELECT st_x(st_centroid(st_transform(st_geometryn(geom, 1), 4326))),
        st_y(st_centroid(st_transform(st_geometryn(geom, 1), 4326))), huc_12
        from flowpaths WHERE scenario = 0
    """, pgconn)
    for i, row in df.iterrows():
        if row['st_y'] > 39.78 and row['st_y'] < 43.7 and row['st_x'] < -94:
            print("%.4f,%.4f,%s" % (row['st_x'], row['st_y'], row['huc_12']))


if __name__ == '__main__':
    main()