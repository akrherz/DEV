"""Generate a diagnostic plot."""

import pandas as pd
from matplotlib.axes import Axes
from pyiem.plot import figure
from pyiem.util import logger
from seaborn import scatterplot

LOG = logger()
VARNAMES = {
    "spring_t_flat_cov": "Avg Spring Flat Cover [fraction]",
    "fall_bio_lai": "Avg Fall LAI [fraction]",
    "tillage_code": "Tillage Code",
    "sand": "Sand [fraction]",
    "erosion_tayr": "Erosion [T/a/yr]",
    "region_angle": "Field Rotation [degN]",
    "tillage_direction": "Tillage Direction [degN]",
}


def make_scatter(
    ax: Axes,
    resultsdf: pd.DataFrame,
    xcol: str,
    ycol: str,
    huecol: str | None = None,
):
    """Do the scatter plot / associated analysis."""
    scatterplot(
        x=xcol,
        y=ycol,
        hue=huecol,
        data=resultsdf,
        ax=ax,
    )
    ax.set_xlabel(VARNAMES.get(xcol, xcol))
    ax.set_ylabel(VARNAMES.get(ycol, ycol))


def main():
    """Go Main."""
    resultsdf = pd.read_csv("results.csv")
    LOG.info("Filtering bad man 090203090201_758.man")
    resultsdf = resultsdf[resultsdf["man_file"] != "090203090201_758.man"]

    fig = figure(
        title="WEPS Sensitivity Analysis",
        subtitle=f"{len(resultsdf.index)} Runs",
        logo="dep",
    )

    ax = fig.add_axes((0.07, 0.6, 0.15, 0.3))
    make_scatter(ax, resultsdf, "sand", "erosion_tayr")

    ax = fig.add_axes((0.3, 0.6, 0.15, 0.3))
    make_scatter(
        ax, resultsdf, "spring_t_flat_cov", "erosion_tayr", "tillage_code"
    )

    ax = fig.add_axes((0.5, 0.6, 0.15, 0.3))
    make_scatter(ax, resultsdf, "fall_bio_lai", "erosion_tayr", "tillage_code")

    ax = fig.add_axes((0.8, 0.6, 0.15, 0.3))
    make_scatter(ax, resultsdf, "erosion_tayr", "wind_file")

    ax = fig.add_axes((0.3, 0.1, 0.2, 0.3))
    make_scatter(ax, resultsdf, "erosion_tayr", "man_file")

    ax = fig.add_axes((0.55, 0.1, 0.15, 0.3))
    make_scatter(ax, resultsdf, "region_angle", "erosion_tayr")

    ax = fig.add_axes((0.8, 0.1, 0.15, 0.3))
    make_scatter(ax, resultsdf, "tillage_direction", "erosion_tayr")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
