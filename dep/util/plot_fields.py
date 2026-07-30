"""Diagnostic"""

import click
import geopandas as gpd
import numpy as np
from matplotlib.colors import BoundaryNorm
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from pyiem.util import logger
from sqlalchemy import text

LOG = logger()


@click.command()
def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("dep") as conn:
        fieldsdf = gpd.read_postgis(
            text(
                """
    select field_id, geom, rectangle_rotation_deg from field
    where scenario_id = 0 and st_ymax(st_transform(geom , 4326)) > 46
    and st_xmin(st_transform(geom, 4326)) < -94
                """
            ),
            conn,
            params={},
            geom_col="geom",
            index_col="field_id",
        )  # type: ignore
    LOG.info("Found %s fields", len(fieldsdf.index))
    minx, miny, maxx, maxy = fieldsdf.to_crs(4326)["geom"].total_bounds
    # minx, miny, maxx, maxy = (-96.874, 46.71621, -96.550, 47.065)
    print(minx, miny, maxx, maxy)
    mp = MapPlot(
        apctx={"_r": "43"},
        # sector="state",
        # state="MN",
        sector="custom",
        south=miny,
        north=maxy,
        west=minx,
        east=maxx,
        title="Field Rotation Angle",
        logo="dep",
        caption="Daily Erosion Project",
        continentalcolor="white",
        stateborderwidth=1,
    )
    bins = np.arange(0, 180.1, 30.0)
    # bins[0] = 0.01
    cmap = get_cmap("jet")
    # cmap.set_under("#0f0")
    norm = BoundaryNorm(bins, cmap.N)
    mp.draw_colorbar(bins, cmap, norm, title="Degrees", extend="neither")
    fieldsdf.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(fieldsdf["rectangle_rotation_deg"].to_numpy())),
        zorder=Z_POLITICAL,
    )
    mp.fig.savefig("field_rotation.png")


if __name__ == "__main__":
    main()
