"""Dump field information."""

import geopandas as gpd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("dep") as conn:
        fields = gpd.read_postgis(
            sql_helper("""
            SELECT st_transform(f.geom, 4326) as geom, landuse,
            management, huc12_fbndid_num as huc12fld, h.huc12_code as huc12
            from field f JOIN huc12 h on (f.huc12_id = h.huc12_id)
            WHERE f.scenario_id = 0 and h.states = 'MN'
        """),
            conn,
            geom_col="geom",
            crs=4326,
        )  # type: ignore
    LOG.info("Found %s fields", len(fields.index))
    fields.to_file("mn_fields.shp")


if __name__ == "__main__":
    main()
