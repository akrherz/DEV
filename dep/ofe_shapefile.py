"""Dump our OFEs to a shapefile."""

import datetime

import geopandas as gpd
from pyiem.util import get_sqlalchemy_conn
from sqlalchemy import text


def main():
    """Go main Go."""
    hucs = ("102300060302 102300060301").split()
    with get_sqlalchemy_conn("idep") as conn:
        ofe = gpd.read_postgis(
            text(
                """
            SELECT o.ofe, o.geom, f.huc_12, f.fpath,
            f.huc_12 || '_' || f.fpath || '_' || o.ofe as id from flowpaths f
            JOIN flowpath_ofes o on (f.fid = o.flowpath) WHERE
            f.scenario = 0 and f.huc_12 = ANY(:hucs)
            """
            ),
            conn,
            params={"hucs": hucs},
            geom_col="geom",
            index_col=None,
        )
    today = datetime.date.today()
    ofe.to_file(f"dep_{today:%Y%m%d}_ofes.shp")


if __name__ == "__main__":
    main()
