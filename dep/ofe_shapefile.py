"""Dump our OFEs to a shapefile."""

from sqlalchemy import text
import geopandas as gpd
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go main Go."""
    hucs = (
        "070801020905 070801030408 070801050302 070801070304 070802011102 "
        "070802050807 070802051502 070802090102 070802090406 071000030704 "
        "071000040910 071000061405 071000070702 071000080502 071000080602 "
        "071000080701 071000081505 102300010607 102300030509 102300031003 "
        "102300031209 102300031403 102300050303 102300070305 102400010302"
    ).split()
    with get_sqlalchemy_conn("idep") as conn:
        ofe = gpd.read_postgis(
            text(
                """
            SELECT o.ofe, o.geom, f.huc_12, f.fpath from flowpaths f
            JOIN flowpath_ofes o on (f.fid = o.flowpath) WHERE
            f.scenario = 0 and f.huc_12 in :hucs
            """
            ),
            conn,
            params={"hucs": tuple(hucs)},
            geom_col="geom",
            index_col=None,
        )
    ofe.to_file("dep_221101_ofes.shp")


if __name__ == "__main__":
    main()
