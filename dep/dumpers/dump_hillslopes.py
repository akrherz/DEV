"""Dump hillslopes to a GIS."""

import geopandas as gpd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("dep") as conn:
        flowpaths = gpd.read_postgis(
            sql_helper("""
            SELECT st_transform(f.geom, 4326) as geom, h.huc12_code as huc_12,
            huc12_fpath_num as fpath
            from flowpath f JOIN huc12 h on (f.huc12_id = h.huc12_id)
            WHERE f.scenario_id = 0 and h.states ~* 'KS'
        """),
            conn,
            geom_col="geom",
            crs=4326,
        )  # type: ignore
    LOG.info("Found %s flowpaths", len(flowpaths.index))
    flowpaths.to_file("ks_flowpaths.shp")


if __name__ == "__main__":
    main()
