"""Accumulated coverage over iemre."""
import os

import numpy as np
import tqdm

import geopandas as gpd
import pandas as pd
from pyiem import iemre
from pyiem.grid.zs import CachingZonalStats
from pyiem.plot import figure_axes
from pyiem.util import get_sqlalchemy_conn, ncopen


def get_data():
    """Get data"""
    with get_sqlalchemy_conn("postgis") as conn:
        states = gpd.read_postgis(
            "SELECT the_geom, state_abbr from states "
            "where state_abbr = 'IA'",
            conn,
            index_col="state_abbr",
            geom_col="the_geom",
        )

    rows = []
    for year in tqdm.tqdm(range(1893, 2022)):
        with ncopen(f"/mesonet/data/iemre/{year}_iemre_daily.nc") as nc:
            high = nc.variables["low_tmpk_12z"]
            if year == 1893:
                hasdata = np.zeros(
                    (nc.dimensions["lat"].size, nc.dimensions["lon"].size)
                )
                czs = CachingZonalStats(iemre.AFFINE)
                czs.gen_stats(hasdata, states["the_geom"])
                for nav in czs.gridnav:
                    grid = np.ones((nav.ysz, nav.xsz))
                    grid[nav.mask] = 0.0
                    jslice = slice(nav.y0, nav.y0 + nav.ysz)
                    islice = slice(nav.x0, nav.x0 + nav.xsz)
                    hasdata[jslice, islice] = np.where(
                        grid > 0, 1, hasdata[jslice, islice]
                    )

            minval = high[200]
            for idx in range(201, 360):
                minval = np.minimum(minval, high[idx])
                rows.append(
                    dict(
                        year=year,
                        doy=idx,
                        count=np.sum(
                            np.logical_and(minval < 273, hasdata > 0)
                        ),
                    )
                )

    df = pd.DataFrame(rows)
    df.to_csv("/tmp/iemre.csv")


def main():
    """go"""
    if not os.path.isfile("/tmp/iemre.csv"):
        get_data()
    df = pd.read_csv("/tmp/iemre.csv")
    iowapts = df["count"].max()
    df["areal"] = df["count"] / iowapts * 100.0
    (fig, ax) = figure_axes(
        apctx={"_r": "43"},
        title=r"Iowa Accumulated Areal Coverage of First Fall sub 32$^\circ$F",
        subtitle="Based on grid analysis between 1893-2021",
    )
    df2 = df.groupby("doy").mean()
    ax.plot(df2.index.values, df2["areal"].values, label="Average", lw=2)
    df2 = df.groupby("doy").max()
    ax.plot(df2.index.values, df2["areal"].values, label="Max", lw=2)
    df2 = df.groupby("doy").min()
    ax.plot(df2.index.values, df2["areal"].values, label="Min", lw=2)
    df2 = df[df["year"] == 2021]
    ax.plot(df2["doy"].values, df2["areal"].values, label="2021", lw=2)
    ax.grid(True)
    ax.legend(loc=2)
    xticks = []
    xticklabels = []
    for dt in pd.date_range("2000/08/25", "2000/12/05"):
        if dt.day in [1, 10, 20]:
            xticks.append(int(dt.strftime("%j")))
            xticklabels.append(f"{dt:%-d %b}")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(235, 336)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_ylabel("Areal Coverage [%]")
    fig.savefig("220923.png")


if __name__ == "__main__":
    main()
