"""Diagnostic"""

from sqlalchemy import text

import geopandas as gpd
from pyiem.plot import MapPlot
from pyiem.reference import Z_POLITICAL
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        huc12df = gpd.read_postgis(
            text(
                """
                select huc12, geom from wbd_huc12 where
                huc12 = '102100100601'
                """
            ),
            conn,
            geom_col="geom",
            index_col="huc12",
        )
        fieldsdf = gpd.read_postgis(
            text(
                """
                select fbndid, geom from fields where scenario = 0
                and huc12 = '102100100601' and fbndid = 171
                """
            ),
            conn,
            geom_col="geom",
            index_col="fbndid",
        )
        fpdf = gpd.read_postgis(
            text(
                """
                select fpath, geom from flowpaths where scenario = 0
                and huc_12 = '102100100601' and fpath = 98
                """
            ),
            conn,
            geom_col="geom",
            index_col="fpath",
        )
    minx, miny, maxx, maxy = fpdf.to_crs(4326)["geom"].total_bounds
    buffer = 0.01
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="custom",
        south=miny - buffer,
        north=maxy + buffer,
        west=minx - buffer,
        east=maxx + buffer,
        title=("HUC12 102100100601 FPATH 98"),
        logo="dep",
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=3,
    )

    huc12df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        ec="k",
        fc="#EEEEEE",
        zorder=Z_POLITICAL,
    )
    fieldsdf.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        ec="r",
        fc="tan",
        zorder=Z_POLITICAL,
    )
    fpdf.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color="g",
        lw=3,
        zorder=Z_POLITICAL,
    )
    # mp.drawcounties()

    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
