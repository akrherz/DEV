"""Dump field information."""

import geopandas as gpd
from dailyerosion.workflows import LANDUSE_DB_RE
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("dep") as conn:
        fields = gpd.read_postgis(
            sql_helper("""
            with data as (
        select o.field_id,
        row_number() over (
            partition by o.field_id ORDER by huc12_fpath_num asc),
        p.huc12_fpath_num, h.huc12_code, f.landuse, f.management,
        st_transform(o.geom, 4326) as geom, c.filepath as clifile,
        g.mukey, f.rectangle_length_m, f.rectangle_width_m,
        f.rectangle_rotation_deg
        from flowpath_ofe o
        JOIN flowpath p on (o.flowpath_id = p.flowpath_id)
        JOIN field f ON (o.field_id = f.field_id)
        JOIN huc12 h on (f.huc12_id = h.huc12_id)
        JOIN climate_file c on (p.climate_file_id = c.climate_file_id)
        JOIN gssurgo g on (o.gssurgo_id = g.gssurgo_id)
        where h.states ~* 'MN'
        and f.scenario_id = 0 and f.scenario_id = p.scenario_id
        and o.ofe = 1 and f.rectangle_length_m > 0
        and not landuse ~ :landuse_db_re)
    select
    field_id as depfldid,
    huc12_code as huc12,
    huc12_fpath_num as flpth_num,
    landuse,
    management as mgt,
    geom from data
    where row_number = 1
        """),
            conn,
            geom_col="geom",
            params={
                "landuse_db_re": LANDUSE_DB_RE,
            },
            crs=4326,
        )  # type: ignore
    LOG.info("Found %s fields", len(fields.index))
    fields.to_file("mn_fields.shp")


if __name__ == "__main__":
    main()
