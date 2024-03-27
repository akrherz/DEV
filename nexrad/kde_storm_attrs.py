"""TVS."""

import numpy as np

from matplotlib.colors import BoundaryNorm
from pandas.io.sql import read_sql
from pyiem import reference
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot
from pyiem.plot.use_agg import plt


def main():
    """Go Main Go."""
    # manual
    west = -96.7
    east = -90.1
    south = 39.34
    north = 44.6
    with get_sqlalchemy_conn("radar") as conn:
        df = read_sql(
            """
        SELECT ST_X(geom) as lon, ST_Y(geom) as lat,
        valid from nexrad_attributes_log
        where nexrad in ('DMX','ARX','DVN','OAX','FSD','EAX','MPX', 'LSX')
        and tvs != 'NONE' and ST_X(geom) > %s and ST_X(geom) < %s
        and ST_Y(geom) > %s and ST_Y(geom) < %s
        """,
            conn,
            params=(
                west,
                east,
                south,
                north,
            ),
        )
    # Create a heatmap of the data using a 100x100 grid over Iowa
    x = np.linspace(west, east, 75)
    y = np.linspace(south, north, 75)
    df["i"] = np.digitize(df["lon"], x)
    df["j"] = np.digitize(df["lat"], y)
    Z = np.zeros((75, 75))
    for idx, row in df.iterrows():
        Z[row["j"], row["i"]] += 1
    print(np.max(Z))

    mp = MapPlot(
        sector="custom",
        north=reference.IA_NORTH,
        south=reference.IA_SOUTH,
        east=reference.IA_EAST,
        west=reference.IA_WEST,
        title="NEXRAD Tornado Vortex Signature Reports",
        subtitle=(
            f"{df['valid'].min():%-d %b %Y} - "
            f"{df['valid'].max():%-d %b %Y}, TVS storm attribute present, "
            f"{len(df.index):,} attributes found."
        ),
    )

    """
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        ["x"] * len(df.index),
        marker="+",
        zorder=20,
        s=40,
        color="k",
        labelbuffer=0,
    )
    """

    cmap = plt.get_cmap("plasma")
    cmap.set_under("None")
    Z = np.ma.masked_where(Z < 0.0001, Z)
    clevs = np.arange(0, 31, 3)
    clevs[0] = 1
    norm = BoundaryNorm(clevs, cmap.N)
    mp.ax.imshow(
        Z,
        interpolation="nearest",
        norm=norm,
        cmap=cmap,
        origin="lower",
        extent=[
            west,
            east,
            south,
            north,
        ],
        zorder=reference.Z_OVERLAY,
    )
    mp.drawcounties()
    mp.plot_values(
        [-93.72, -96.37, -91.18, -90.57, -96.72],
        [41.72, 41.32, 43.82, 41.6, 43.58],
        ["X", "X", "X", "X", "X"],
        textsize=18,
        color="r",
        zorder=reference.Z_OVERLAY + 1,
    )
    mp.draw_colorbar(clevs, cmap, norm, title="Count")
    mp.fig.savefig("240327.png")


if __name__ == "__main__":
    main()
