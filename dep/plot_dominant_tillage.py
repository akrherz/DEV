"""Plot what we have in myhucs.csv"""

import geopandas as gpd
from matplotlib import colors as mpcolors
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot
from pyiem.reference import Z_POLITICAL
from sqlalchemy import text


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        df = gpd.read_postgis(
            text(
                """
                select huc_12, simple_geom, dominant_tillage from
                huc12 where scenario = 0 and states ~* 'IA'
                """
            ),
            conn,
            geom_col="simple_geom",
            index_col="huc_12",
        )
    # df = df.fillna(0)
    # df["ratio"] = df["runoff"] / df["precip"] * 100.0
    # df2 = df[df["precip"] >= 5]
    minx, miny, maxx, maxy = df.to_crs(4326)["simple_geom"].total_bounds
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="custom",
        south=miny,
        north=maxy,
        west=minx,
        east=maxx,
        title=("Daily Erosion Project:: Dominant Tillage Practice by HUC12"),
        # subtitle="for DEP HUC12s with at least 5mm of precipitation",
        logo="dep",
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=3,
    )
    cmap = mpcolors.ListedColormap(name="my", colors=["blue", "yellow", "red"])
    bins = [1, 2, 4, 6]
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(df["dominant_tillage"])),
        zorder=Z_POLITICAL,
    )
    mp.drawcounties()
    mp.draw_colorbar(
        bins, cmap, norm, clevlabels=["", "", "", ""], extend="neither"
    )
    mp.fig.text(
        0.95,
        0.2,
        "No Till",
        rotation=90,
        fontsize=14,
        va="center",
        ha="center",
    )
    mp.fig.text(
        0.95,
        0.5,
        "Conservation",
        rotation=90,
        fontsize=14,
        va="center",
        ha="center",
    )
    mp.fig.text(
        0.95,
        0.8,
        "Intensive",
        rotation=90,
        fontsize=14,
        va="center",
        ha="center",
    )

    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
