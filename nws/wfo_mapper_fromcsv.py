"""Generic plotter"""

from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot

# import numpy as np
import pandas as pd


def main():
    """Go Main"""
    df = pd.read_csv("wfo.csv", index_col="wfo")
    # df["count"] = 100. - df["count"]
    vals = df["count"].to_dict()
    # bins = list(range(12))
    # bins = np.arange(2011, 2021, 1)
    # bins = [0, 0.1, 0.2, 0.5, 0.75, 1, 2, 5, 10]
    bins = [1, 5, 10, 25, 50, 75, 100, 125]
    # bins = np.arange(0, 101, 10)
    cmap = plt.get_cmap("Blues")
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        twitter=True,
        title=(
            "2016-2021 Average Word Count within "
            "Overview of WSW non-cancel/expire Product"
        ),
        subtitle=("based on IEM archives"),
    )
    mp.fill_cwas(
        vals,
        bins=bins,
        lblformat="%.0f",  # , labels=labels,
        cmap=cmap,
        ilabel=True,  # clevlabels=clevlabels,
        units="count",
        extend="neither",
        spacing="proportional",
    )

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
