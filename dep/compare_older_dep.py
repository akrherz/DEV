"""Compare with older DEP output."""

# stdlib
import glob
import os

import numpy as np

# Third party
from tqdm import tqdm

import geopandas as gpd
import matplotlib.colors as mpcolors
import pandas as pd
from pyiem.dep import read_env
from pyiem.plot import MapPlot, figure_axes, get_cmap
from pyiem.util import get_sqlalchemy_conn


def plot2():
    """plot stuff."""
    df = pd.read_csv(
        "/tmp/compare_older_dep.csv",
        dtype={"huc12": str},
    ).set_index("huc12")
    (fig, ax) = figure_axes(
        logo="dep", title="DEP 2007-2016 Yearly Detachment by Model Revision"
    )
    df[["old_avg", "new_avg"]].plot.kde(ax=ax)
    ax.set_xlim(0, 25)
    ax.grid(True)
    ax.set_xlabel("2007-2016 Average Detachment (T/a/yr)")

    fig.savefig("/tmp/test.png")


def plotmap():
    """Plot some stuff."""
    df = pd.read_csv(
        "/tmp/compare_older_dep.csv",
        dtype={"huc12": str},
    ).set_index("huc12")
    with get_sqlalchemy_conn("idep") as conn:
        gdf = gpd.read_postgis(
            "SELECT simple_geom, huc_12 from huc12 where scenario = 0",
            conn,
            geom_col="simple_geom",
            index_col="huc_12",
        )
    gdf = gdf.join(df).dropna()
    gdf["change"] = (gdf["new_5t"] / gdf["new_fpcount"]) * 100.0 - (
        gdf["old_5t"] / gdf["old_fpcount"]
    ) * 100.0
    bins = np.arange(-25, 26, 5)
    cmap = get_cmap("RdBu")
    cmap.set_over("white")
    cmap.set_under("thistle")
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    gdf["color"] = list(cmap(norm(gdf["change"])))

    mp = MapPlot(
        logo="dep",
        sector="custom",
        west=-99,
        north=45,
        south=37,
        east=-89,
        title="DEP 2007-2016 Percent Points Change in Flowpaths > 5 T/a/yr",
        subtitle="May 2022 minus circa 2017",
        caption="Daily Erosion Project",
    )
    gdf.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        color=gdf["color"],
        zorder=20,
    )
    mp.draw_colorbar(bins, cmap, norm, units="% Change", extend="both")
    mp.fig.savefig("/tmp/test.png")


def plot():
    """Compare some things."""
    df = pd.read_csv("/tmp/compare_older_dep.csv")
    (fig, ax) = figure_axes(
        logo="dep",
        title="DEP 2007-2016 Yearly Max Flowpath Detachment by Model Revision",
    )
    ax.scatter(df["old_max"], df["new_max"])
    ax.plot([0, 200], [0, 200])
    ax.axvline(df["old_max"].mean(), color="r")
    ax.text(df["old_max"].mean(), 175, f"Avg: {df['old_max'].mean():.2f}")
    ax.text(175, df["new_max"].mean(), f"Avg: {df['new_max'].mean():.2f}")
    ax.axhline(df["new_max"].mean(), color="r")
    ax.set_xlabel("2008-2016 Max Detachment (T/a/yr) [Circa 2017]")
    ax.set_ylabel("2008-2016 Max Detachment (T/a/yr) [May 2022]")
    ax.grid(True)
    ax.set_xlim(-0.5, 200)
    ax.set_ylim(-0.5, 200)
    fig.savefig("/tmp/test.png")


def main():
    """Go Main Go."""
    os.chdir("/i/0_161205/env")
    res = []
    progress = tqdm(os.listdir("."))
    for huc8 in progress:
        progress.set_description(f"{huc8}")
        for huc4 in os.listdir(huc8):
            if not os.path.isdir(f"/i/0/env/{huc8}/{huc4}"):
                print(f"No current data for {huc8}/{huc4}")
                continue
            current = []
            for fn in glob.glob(f"/i/0/env/{huc8}/{huc4}/*.env"):
                df = read_env(fn)
                df = df[df["year"] < 2017]
                current.append(df["av_det"].sum() * 4.463 / 10.0)  # T/a/yr

            older = []
            for fn in glob.glob(f"/i/0_161205/env/{huc8}/{huc4}/*.env"):
                try:
                    df = read_env(fn)
                except Exception as exp:
                    print(exp, fn)
                    continue
                df = df[df["year"] < 2017]
                val = df["av_det"].sum() * 4.463 / 10.0  # T/a/yr
                older.append(val)
            if not older:
                print(f"No older data for {huc8}/{huc4}, aborting")
                return
            if not current:
                print(f"No current data for {huc8}/{huc4}, skipping")
                continue

            older = np.array(older)
            current = np.array(current)
            res.append(
                {
                    "huc12": f"{huc8}{huc4}",
                    "old_fpcount": len(older),
                    "new_fpcount": len(current),
                    "old_lt0.1": np.sum(older < 0.1),
                    "new_lt0.1": np.sum(current < 0.1),
                    "old_5t": np.sum(older >= 5),
                    "new_5t": np.sum(current >= 5),
                    "old_avg": older.mean(),
                    "new_avg": current.mean(),
                    "old_std": older.std(),
                    "new_std": current.std(),
                    "old_max": older.max(),
                    "new_max": current.max(),
                    "old_min": older.min(),
                    "new_min": current.min(),
                }
            )

    df = pd.DataFrame(res)
    print(df["old_avg"].describe())
    print(df["new_avg"].describe())
    df.to_csv("/tmp/compare_older_dep.csv")


if __name__ == "__main__":
    plot()
