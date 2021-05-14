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
    data = (df["count"] - df["avg"]).round(0)
    vals = data.to_dict()
    bins = list(range(-100, 101, 25))
    # bins = np.arange(2012, 2022, 1)
    # bins = [0, 0.1, 0.2, 0.5, 0.75, 1, 2, 5, 10]
    # bins = [1, 5, 10, 25, 50, 75, 100, 125]
    # bins = np.arange(0, 17, 2)
    cmap = get_cmap("RdBu")
    # cmap.set_over("lightyellow")
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        twitter=True,
        title=(
            "2021 Departure of Total Severe T'Storm + Tornado Warnings Issued vs 20 Year Average"
        ),
        subtitle=(
            "based on unofficial IEM archives over 1 Jan - 13 May, 2002-2021, nationwide depature %.0f warnings"
            % (data.sum())
        ),
    )
    mp.fill_cwas(
        vals,
        bins=bins,
        lblformat="%.0f",  # , labels=labels,
        cmap=cmap,
        ilabel=True,  # clevlabels=clevlabels,
        units="departure count",
        extend="neither",
        spacing="proportional",
    )

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
