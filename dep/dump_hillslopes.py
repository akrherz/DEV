"""Shrug, just do as I am told."""

from geopandas import read_postgis
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as pgconn:
        df = read_postgis(
            """
            SELECT st_transform(geom, 4326) as geom, huc_12, fpath
            from flowpaths WHERE scenario = 0
        """,
            pgconn,
        )
    df.to_file("flowpaths.shp")


if __name__ == "__main__":
    main()
