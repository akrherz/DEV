"""Generate a diagnostic plot."""

import pandas as pd
from matplotlib.axes import Axes
from pyiem.plot import figure


def make_scatter(ax: Axes, resultsdf: pd.DataFrame, xcol: str, ycol: str):
    """Do the scatter plot / associated analysis."""
    ax.scatter(
        resultsdf[xcol].values,
        resultsdf[ycol].values,
        marker="o",
    )
    ax.set_xlabel(xcol)
    ax.set_ylabel(ycol)
    ax.grid(True)


def main():
    """Go Main."""
    resultsdf = pd.read_csv("results.csv")

    fig = figure(
        title="WEPS Sensitivity Analysis",
        subtitle=f"{len(resultsdf.index)} Runs",
        logo="dep",
    )

    ax = fig.add_axes((0.1, 0.6, 0.4, 0.3))
    make_scatter(ax, resultsdf, "sand", "erosion_tayr")

    ax = fig.add_axes((0.55, 0.6, 0.4, 0.3))
    make_scatter(ax, resultsdf, "tillage_code", "erosion_tayr")

    ax = fig.add_axes((0.3, 0.1, 0.2, 0.3))
    make_scatter(ax, resultsdf, "erosion_tayr", "man_file")

    ax = fig.add_axes((0.75, 0.1, 0.2, 0.3))
    make_scatter(ax, resultsdf, "erosion_tayr", "region_angle")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
