"""Generic plotter"""

from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot, get_cmap

import numpy as np
import pandas as pd


def main():
    """Go Main"""
    df = pd.read_csv("wfo.csv", index_col=None)
    df["wfo"] = df["wfo"].apply(lambda x: x[1:])
    df = df.set_index("wfo")
    print(df)
    # df["count"] = 100. - df["count"]
    vals = df["year"].to_dict()
    # bins = list(range(12))
    bins = np.arange(2012, 2022, 1)
    # bins = [0, 0.1, 0.2, 0.5, 0.75, 1, 2, 5, 10]
    # bins = [1, 5, 10, 25, 50, 75, 100, 125]
    # bins = np.arange(0, 17, 2)
    cmap = get_cmap("Greens")
    cmap.set_over("lightyellow")
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        twitter=True,
        title=(
            "Year of Last Hazardous Weather Outlook (HWO) by NWS Forecast Office"
        ),
        subtitle=("based on IEM processing ending 19 April 2021"),
    )
    mp.fill_cwas(
        vals,
        bins=bins,
        lblformat="%.0f",  # , labels=labels,
        cmap=cmap,
        ilabel=True,  # clevlabels=clevlabels,
        units="count",
        extend="max",
        spacing="proportional",
    )

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
