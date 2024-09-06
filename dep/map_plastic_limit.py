"""Plot our plastic limit."""

import numpy as np
from sqlalchemy import text

import geopandas as gpd
import matplotlib.colors as mpcolors
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_OVERLAY


def main():
    """Go main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        gdf = gpd.read_postgis(
            text(
                """
            with ofes as (
                select st_pointn(o.geom, 1) as pt, gssurgo_id
                from flowpath_ofes o
                JOIN flowpaths f on (o.flowpath = f.fid) WHERE f.scenario = 0
            )
            SELECT pt, plastic_limit -
                (wepp_min_sw + 0.42 * (wepp_max_sw - wepp_min_sw)) as toplot
            from gssurgo g JOIN ofes o on (g.id = o.gssurgo_id)
            """
            ),
            conn,
            params={},
            geom_col="pt",
            index_col=None,
            crs=5070,
        )
    print(gdf["toplot"].describe())
    minx, miny, maxx, maxy = gdf["pt"].to_crs(4326).total_bounds
    buffer = 0.1
    mp = MapPlot(
        title=(
            "WEPP/DEP Plastic Limit - (Min + 0.42(Max-Min)) "
            "0-10cm Soil Moisture"
        ),
        # subtitle=(
        #    r"$PL = 14.22 + 0.005 * clay^2 + 3.63 * om - 0.048 * clay * om$"
        # ),
        logo="dep",
        sector="custom",
        west=minx - buffer,
        north=maxy + buffer,
        south=miny - buffer,
        east=maxx + buffer,
        caption="Daily Erosion Project",
    )
    bins = np.arange(-15, 15.1, 5.0)
    # bins = np.arange(10, 60.1, 10.0)
    cmap = get_cmap("RdBu")
    cmap.set_over("yellow")
    cmap.set_under("tan")
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    gdf.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        color=cmap(norm(gdf["toplot"])),
        markersize=1,
        zorder=Z_OVERLAY,
    )
    overdf = gdf[gdf["toplot"] > 60]
    if not overdf.empty:
        overdf.to_crs(mp.panels[0].crs).plot(
            ax=mp.panels[0].ax,
            aspect=None,
            color=cmap(norm(overdf["toplot"])),
            markersize=1,
            zorder=Z_OVERLAY + 1,
        )
    mp.draw_colorbar(bins, cmap, norm, units="%")
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
