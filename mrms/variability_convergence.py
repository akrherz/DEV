"""Compute some metrics on precipitation washing out."""

from datetime import date

import numpy as np
from affine import Affine
from tqdm import tqdm

import geopandas as gpd
from pyiem import iemre
from pyiem.grid.zs import CachingZonalStats
from pyiem.plot import figure, plt
from pyiem.util import get_sqlalchemy_conn, mm2inch, ncopen


def main():
    """Go Please"""
    # Get story county geom
    with get_sqlalchemy_conn("postgis") as conn:
        counties = gpd.read_postgis(
            """
        SELECT geom from ugcs where ugc = 'IAC169' limit 1
        """,
            conn,
            geom_col="geom",
        )
    czs = CachingZonalStats(
        Affine(0.004167, 0.0, -97.154167, 0.0, -0.004167, 44.533683)
    )

    fig = figure(
        title=(
            "2023 Iowa Flood Center Grid Cell Backward Accumulation for "
            "Story County"
        ),
        subtitle="based on 9492 0.004x0.004 degree grid cells covering county",
        figsize=(8, 6),
    )
    ax = fig.add_axes([0.1, 0.65, 0.85, 0.23])
    ax.set_ylabel("Accum Precip [inch]")
    ax.grid(True)
    ax3 = fig.add_axes([0.1, 0.36, 0.85, 0.22])
    ax3.set_ylabel("Accum Precip\nRange [inch]")
    ax3.grid(True)
    ax2 = fig.add_axes([0.1, 0.05, 0.85, 0.22])
    ax2.set_ylabel("Grid Cells [%]")

    with ncopen("/mesonet/data/iemre/2023_ifc_daily.nc") as nc:
        tidx0 = iemre.daily_offset(date(2023, 9, 19))
        p01d = nc.variables["p01d"]
        pday = p01d[tidx0, :, :]
        czs.gen_stats(np.flipud(pday), counties["geom"])
        nav = czs.gridnav[0]
        # top-down reminder
        jslice = slice(nav.y0, nav.y0 + nav.ysz)
        islice = slice(nav.x0, nav.x0 + nav.xsz)
        print(nav.xsz * nav.ysz)
        total_precip = np.flipud(pday)[jslice, islice]
        cmap = plt.get_cmap("jet")
        colors = cmap(np.ravel(total_precip) / np.max(total_precip))
        gridlen = total_precip.shape[0] * total_precip.shape[1]
        y = []
        yrng = []
        progress = tqdm(list(range(tidx0 - 1, -1, -1)))
        for tidx in progress:
            progress.set_description(f"{tidx} {np.max(total_precip):.2f}")
            total_precip += np.ma.filled(
                np.flipud(p01d[tidx])[jslice, islice], 0
            )
            ax.scatter(
                [tidx0 - tidx] * gridlen,
                mm2inch(np.ravel(total_precip)),
                color=colors,
            )
            # percentage of total_precip points within +/- 5% of median
            median = np.median(total_precip)
            cnt = np.sum(
                np.logical_and(
                    total_precip >= (median * 0.95),
                    total_precip <= (median * 1.05),
                )
            )
            y.append(cnt / float(gridlen) * 100.0)
            yrng.append(np.max(total_precip) - np.min(total_precip))
        ax3.plot(range(len(y)), mm2inch(yrng))
        ax2.set_title("Percentage of grid cells within +/- 5% of median")
        ax2.plot(range(len(y)), y)
        ax2.grid(True)
        ax2.set_ylim(0, 100)
        ax2.set_yticks([0, 10, 25, 50, 75, 90, 100])
        ax2.set_xticks([18, 48, 79, 109, 140, 170, 201, 229, 260])
        ax2.set_xticklabels(
            ["Sep", "Aug", "Jul", "Jun", "May", "Apr", "Mar", "Feb", "Jan"]
        )
        ax3.set_xticks([18, 48, 79, 109, 140, 170, 201, 229, 260])
        ax3.set_xticklabels(
            ["Sep", "Aug", "Jul", "Jun", "May", "Apr", "Mar", "Feb", "Jan"]
        )
        ax.set_xticks([18, 48, 79, 109, 140, 170, 201, 229, 260])
        ax.set_xticklabels(
            ["Sep", "Aug", "Jul", "Jun", "May", "Apr", "Mar", "Feb", "Jan"]
        )
        ax.set_xlim(-1, tidx0)
        ax2.set_xlim(-1, tidx0)
        ax3.set_xlim(-1, tidx0)

    fig.savefig("230920.png")


if __name__ == "__main__":
    main()
