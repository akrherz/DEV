"""Investigate a stability theory."""

import calendar
import glob
from random import randint

import pandas as pd
from dailyerosion.io.dep import read_wb
from pyiem.plot import figure_axes


def main():
    """Go Main Go."""
    dfs = []
    for wbfn in glob.glob("/i/0/wb/07080207/0602/*.wb"):
        df = read_wb(wbfn)
        df = df[(df["ofe"] == 1) & (df["date"].dt.year == 2025)]
        df["fp"] = wbfn.split("_")[1][:-3]
        dfs.append(df)

    df = pd.concat(dfs)
    # Rank sw1 by jday
    df["rank"] = df.groupby("jday")["sw1"].rank()
    # Pick a random flowpath
    randfp = df["fp"].unique().tolist()[randint(0, len(dfs) - 1)]

    fig, ax = figure_axes(
        title=(
            "Daily Erosion Project:: South Fork 2025\n"
            f"Flowpath #{randfp} 0-10 cm Soil Moisture Rank by Day"
        ),
        logo=None,
        figsize=(8, 6),
    )
    for fp in df["fp"].unique():
        subdf = df[df["fp"] == fp]
        ax.plot(
            subdf["jday"],
            subdf["rank"],
            label=fp if fp == randfp else None,
            lw=2 if fp == randfp else 0.5,
            color="r" if fp == randfp else "tan",
            zorder=2 if fp == randfp else 1,
        )
    ax.grid(True)
    ax.legend()
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_ylabel("Flowpath Rank over HUC12 (1=driest)")
    ax.set_xlabel("Day of 2025")
    outpng = f"dep_sm_rank_{randfp}.png"
    print(outpng)
    fig.savefig(outpng)


if __name__ == "__main__":
    main()
