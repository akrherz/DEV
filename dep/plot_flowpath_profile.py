"""Diagnostic"""

import click
import geopandas as gpd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes
from shapely.geometry import Point
from sqlalchemy import text


@click.command()
@click.option("--huc12", help="HUC12 to plot")
@click.option("--flowpath", type=int, help="Fpath")
def main(huc12, flowpath):
    """Go Main Go."""
    params = {
        "huc12": huc12,
        "fpath": flowpath,
    }
    with get_sqlalchemy_conn("idep") as conn:
        ofedf = gpd.read_postgis(
            text(
                """
                select ofe, o.real_length, o.geom from
                flowpaths f JOIN flowpath_ofes o on (f.fid = o.flowpath)
                where scenario = 0
                and huc_12 = :huc12 and fpath = :fpath ORDER by ofe
                """
            ),
            conn,
            params=params,
            geom_col="geom",
            index_col="ofe",
        )
    fig, ax = figure_axes(
        title=f"HUC12 {huc12} Flowpath {flowpath} Profile",
        logo="dep",
        figsize=(8, 6),
    )
    # set ax aspect to linear so there is no distortion
    # ax.set_aspect("equal")
    start_point = None
    for ofe, row in ofedf.iterrows():
        if start_point is None:
            start_point = Point(*row["geom"].coords[0])
        x = []
        y = []
        for coord in row["geom"].coords:
            x.append(Point(coord).distance(start_point))
            y.append(coord[2])
        ax.plot(x, y, label=f"OFE {ofe}", lw=3)
    ax.legend(ncol=3)  # loc=(0.5, 1.1))
    ax.grid(True)
    ax.set_ylabel("Elevation [m]")
    ax.set_xlabel("Distance [m]")
    # Increase ylim by 10% to give some space
    delta = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.3
    ax.set_ylim(ax.get_ylim()[0] - delta, ax.get_ylim()[1] + delta)

    fig.savefig(f"/tmp/flowpath_{huc12}_{flowpath}.png")


if __name__ == "__main__":
    main()
