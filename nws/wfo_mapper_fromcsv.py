"""Generic plotter"""

from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot, get_cmap

import numpy as np
import pandas as pd


def main():
    """Go Main"""
    df = pd.read_csv("wfo.csv", index_col=None)
    # df["wfo"] = df["wfo"].apply(lambda x: x[1:])
    df = df.set_index("wfo")
    print(df)
    # df["count"] = 100. - df["count"]
    # data = (df["count"] - df["avg"]).round(0).astype(int)
    # data = (df["rank"]).round(0).astype(int)
    vals = ((df["count"] - df["avg"]) / df["stddev"]).to_dict()
    print(vals["PSR"])
    bins = list(range(-100, 101, 25))
    # bins = np.arange(2012, 2022, 1)
    # bins = [0, 0.1, 0.2, 0.5, 0.75, 1, 2, 5, 10]
    # bins = [1, 5, 10, 25, 50, 75, 100, 125]
    bins = np.arange(-3.1, 3.1, 0.5)
    cmap = get_cmap("RdBu")
    # cmap.set_over("lightyellow")
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        twitter=True,
        title=(
            "2021 Standardized Departure of Total Severe T'Storm + Tornado Warnings Issued "
            "vs Past 20 Years"
        ),
        subtitle=(
            "based on unofficial IEM archives over 1 Jan - 2 June, 2002-2021 "
            # f"nationwide depature {data.sum():.0f} warnings"
            # f"rank of 1 is least number"
        ),
    )
    mp.fill_cwas(
        vals,
        bins=bins,
        lblformat="%.1f",  # , labels=labels,
        labelbuffer=0,
        cmap=cmap,
        ilabel=True,  # clevlabels=clevlabels,
        units="sigma",
        extend="both",
        spacing="proportional",
    )

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
