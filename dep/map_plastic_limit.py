"""Plot our plastic limit."""

import numpy as np
from sqlalchemy import text
import geopandas as gpd
import matplotlib.colors as mpcolors
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        gdf = gpd.read_postgis(
            text(
                """
            with ofes as (
                select st_geometryn(o.geom, 1) as pt, gssurgo_id
                from flowpath_ofes o
                JOIN flowpaths f on (o.flowpath = f.fid) WHERE f.scenario = 0
            )
            SELECT pt, g.plastic_limit
            from gssurgo g JOIN ofes o on (g.id = o.gssurgo_id)
            """
            ),
            conn,
            params={},
            geom_col="pt",
            index_col=None,
        )
    print(gdf["plastic_limit"].describe())
    minx, miny, maxx, maxy = gdf["pt"].to_crs(4326).total_bounds
    buffer = 0.1
    mp = MapPlot(
        title="Plastic Limit for Soils Modelled by DEP",
        subtitle=(
            r"$PL = 14.22 + 0.005 * clay^2 + 3.63 * om - 0.048 * clay * om$"
        ),
        logo="dep",
        sector="custom",
        west=minx - buffer,
        north=maxy + buffer,
        south=miny - buffer,
        east=maxx + buffer,
        caption="Daily Erosion Project",
    )
    bins = np.arange(10, 60.1, 10.0)
    cmap = get_cmap("jet")
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    gdf.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        color=cmap(norm(gdf["plastic_limit"])),
    )
    mp.draw_colorbar(bins, cmap, norm, units="%")
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
