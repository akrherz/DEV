"""Look at how things changed."""

import pandas as pd
from geopandas import read_postgis
from matplotlib import colors as mpcolors
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot
from pyiem.reference import Z_POLITICAL
from sqlalchemy import text


def main():
    """Go Main Go."""
    old = pd.read_csv(
        "/tmp/huc12_old.db",
        sep="\t",
        names=["huc_12", "dominant_tillage"],
        na_values=["\\N"],
        dtype={"huc_12": str},
    ).set_index("huc_12")
    old["dominant_tillage"] = pd.to_numeric(
        old["dominant_tillage"], errors="coerce"
    )

    with get_sqlalchemy_conn("idep") as conn:
        df = read_postgis(
            text(
                """
                select huc_12, simple_geom, dominant_tillage from
                huc12 where scenario = 0
                """
            ),
            conn,
            geom_col="simple_geom",
            index_col="huc_12",
        )
    df["old"] = old["dominant_tillage"]
    df["change"] = df["dominant_tillage"] - df["old"]
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
        title=("27 Sep 2023 Change in Dominant Tillage vs July 2023"),
        # subtitle="for DEP HUC12s with at least 5mm of precipitation",
        logo="dep",
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=3,
    )
    cmap = mpcolors.ListedColormap(
        name="my", colors=["purple", "blue", "yellow", "orange", "red"]
    )
    bins = [-3, -2, -1, 1, 2, 3]
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(df["change"])),
        zorder=Z_POLITICAL,
    )
    mp.drawcounties()
    mp.draw_colorbar(
        bins, cmap, norm, clevlabels=["", "", "", "", "", ""], extend="neither"
    )
    mp.fig.text(
        0.95,
        0.2,
        "2 Cat Decrease",
        rotation=90,
        fontsize=14,
        va="center",
        ha="center",
    )
    mp.fig.text(
        0.95,
        0.5,
        "No Change",
        rotation=90,
        fontsize=14,
        va="center",
        ha="center",
    )
    mp.fig.text(
        0.95,
        0.8,
        "2 Cat Increase",
        rotation=90,
        fontsize=14,
        va="center",
        ha="center",
    )

    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
