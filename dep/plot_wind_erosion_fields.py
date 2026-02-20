"""Diagnostic"""

from datetime import datetime

import click
import geopandas as gpd
import numpy as np
from dailyerosion.reference import KG_M2_TO_TON_ACRE
from matplotlib.colors import BoundaryNorm
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from sqlalchemy import text

GRAPH_HUC12 = (
    "090201081101 090201081102 090201060605 102702040203 101500041202 "
    "090203010403 070200070501 070102050503 090203030703 090203030702 "
    "090203030304 090201081002 070102020203 070200080101 101702040106"
).split()


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="Date to plot")
def main(dt: datetime):
    """Go Main Go."""
    dt = dt.date()
    with get_sqlalchemy_conn("idep") as conn:
        huc12df = gpd.read_postgis(
            text(
                """
    select simple_geom, huc_12 from huc12 where huc_12 = Any(:hucs)
    and scenario = 0
                """
            ),
            conn,
            params={"hucs": GRAPH_HUC12},
            geom_col="simple_geom",
            index_col="huc_12",
        )  # type: ignore
        fieldsdf = gpd.read_postgis(
            text(
                """
    select fbndid, erosion_kgm2, max_wmps, geom from
    field_wind_erosion_results r
    join fields f on (r.field_id = f.field_id) where r.valid = :dt
    and erosion_kgm2 >= 0
                """
            ),
            conn,
            params={"dt": dt},
            geom_col="geom",
            index_col="fbndid",
        )  # type: ignore
    fieldsdf["erosion_ta"] = fieldsdf["erosion_kgm2"] * KG_M2_TO_TON_ACRE
    minx, miny, maxx, maxy = fieldsdf.to_crs(4326)["geom"].total_bounds
    minx, miny, maxx, maxy = (-96.874, 46.71621, -96.750, 46.965)
    print(minx, miny, maxx, maxy)
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="custom",
        south=miny,
        north=maxy,
        west=minx,
        east=maxx,
        title=f"Wind Erosion [T/a] for {dt}",
        logo="dep",
        caption="Daily Erosion Project",
        continentalcolor="white",
        stateborderwidth=1,
    )
    bins = np.arange(14, 20.1, 0.25)
    # bins[0] = 0.01
    cmap = get_cmap("plasma")
    cmap.set_under("#0f0")
    norm = BoundaryNorm(bins, cmap.N)
    mp.draw_colorbar(bins, cmap, norm, title="T/a", extend="both")
    fieldsdf.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(fieldsdf["max_wmps"].to_numpy())),
        zorder=Z_POLITICAL,
    )
    huc12df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        ec="k",
        fc="None",
        zorder=Z_POLITICAL + 1,
        linewidth=2,
    )
    mp.fig.savefig(f"field_wind_erosion_{dt}_zoom.png")


if __name__ == "__main__":
    main()
