"""Shrug, just do as I am told."""

import geopandas as gpd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        flowpaths = gpd.read_postgis(
            sql_helper("""
            SELECT st_transform(f.geom, 4326) as geom, f.huc_12, fpath
            from flowpaths f, huc12 h WHERE f.scenario = 0 and h.scenario = 0
            and h.states ~* 'KS' and f.huc_12 = h.huc_12
        """),
            conn,
            geom_col="geom",
            crs=4326,
        )  # type: ignore
    LOG.info("Found %s flowpaths", len(flowpaths.index))
    flowpaths.to_file("ks_flowpaths.shp")


if __name__ == "__main__":
    main()
