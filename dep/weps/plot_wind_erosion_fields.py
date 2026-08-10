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


@click.command()
@click.option(
    "--date", "dt", type=click.DateTime(), help="Date to plot", required=True
)
def main(dt: datetime):
    """Go Main Go."""
    dt = dt.date()
    with get_sqlalchemy_conn("dep") as conn:
        fieldsdf = gpd.read_postgis(
            text(
                """
    with myfields as (
        select f.field_id, f.geom from
        field f JOIN field_wind_erosion_results r on (f.field_id = r.field_id)
        where r.valid = '2026-05-12'
    ), myday as (
        select field_id, max_wind_speed_mps, erosion_kgm2 from
        field_wind_erosion_results where valid = :dt
    )
    select f.field_id as fbndid,
    coalesce(erosion_kgm2, 0) as erosion_kgm2, max_wind_speed_mps, f.geom from
    myfields f LEFT JOIN myday r on (f.field_id = r.field_id)
    ORDER by erosion_kgm2 asc
                """
            ),
            conn,
            params={"dt": dt},
            geom_col="geom",
            index_col="fbndid",
        )  # type: ignore
    fieldsdf["erosion_ta"] = fieldsdf["erosion_kgm2"] * KG_M2_TO_TON_ACRE
    stats = fieldsdf["erosion_ta"].describe(
        percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]
    )

    minx, miny, maxx, maxy = fieldsdf.to_crs(4326)["geom"].total_bounds
    # minx, miny, maxx, maxy = (-96.874, 46.71621, -96.550, 47.065)
    print(minx, miny, maxx, maxy)
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="state",
        state="MN",
        # sector="custom",
        # south=miny,
        # north=maxy,
        # west=minx,
        # east=maxx,
        title=f"Wind Erosion [T/a] for {dt}",
        subtitle=(
            f"Field mean: {stats['mean']:.1f} T/a, "
            f" 95%: {stats['95%']:.1f} T/a,"
            f" max: {stats['max']:.1f} T/a. Fields plotted as points."
        ),
        logo="dep",
        caption="Daily Erosion Project",
        continentalcolor="white",
        stateborderwidth=1,
    )
    bins = np.arange(0, 10.1, 0.5)
    bins[0] = 0.01
    cmap = get_cmap("plasma")
    cmap.set_under("tan")
    norm = BoundaryNorm(bins, cmap.N)
    mp.draw_colorbar(bins, cmap, norm, title="T/a", extend="both")
    pts = fieldsdf.to_crs(mp.panels[0].crs).centroid
    mp.panels[0].ax.scatter(
        pts.x,
        pts.y,
        c=cmap(norm(fieldsdf["erosion_ta"].to_numpy())),
        s=10,
        edgecolor="None",
        zorder=Z_POLITICAL + 1,
    )
    """
    fieldsdf.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(fieldsdf["erosion_ta"].to_numpy())),
        zorder=Z_POLITICAL,
    )
    """
    mp.fig.savefig(f"field_wind_erosion_{dt}.png")


if __name__ == "__main__":
    main()
