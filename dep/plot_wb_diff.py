"""Plots."""
import calendar

import pandas as pd
from pyiem.dep import read_wb, read_env
from pyiem.plot.use_agg import plt


def main():
    """Go Main Go."""
    orig = read_wb("/tmp/orig.wb").set_index("date")
    neww = read_wb("/tmp/new.wb").set_index("date")

    env_orig = read_env("/tmp/orig.env").set_index("date")
    env_neww = read_env("/tmp/new.env").set_index("date")

    fig, axes = plt.subplots(3, 1, figsize=(8, 9))
    ax = axes[0]
    ax.set_title(
        "2007-2021 WEPP 1 Hillslope Difference Test\n"
        "Snowfall by Dew Point (new) minus Snowfall 10x Rain (old)"
    )
    diff = (
        neww.groupby(neww.index.month).mean()["sw"]
        - orig.groupby(orig.index.month).mean()["sw"]
    )
    ax.bar(diff.index.values, diff.values)
    ax.set_ylabel(r"$\Delta$ Total Soil Moisture $mm$")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)

    ax = axes[1]
    diff = (
        env_neww.groupby("month").sum()["runoff"]
        - env_orig.groupby("month").sum()["runoff"]
    ) / 15.0
    ax.bar(diff.index.values, diff.values)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_ylabel(r"$\Delta$ Monthly Runoff $mm$")

    ax = axes[2]
    diff = (
        (
            env_neww.groupby("month").sum()["sed_del"]
            - env_orig.groupby("month").sum()["sed_del"]
        )
        / 15.0
        / 45.0
    )  # len of hillslope
    ax.bar(diff.index.values, diff.values)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_ylabel(r"$\Delta$ Monthly Sed Delivery $kg m^{-2}$")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
