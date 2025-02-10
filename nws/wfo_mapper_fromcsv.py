"""Generic plotter"""

import pandas as pd
from pyiem.plot import MapPlot, get_cmap


def main():
    """Go Main"""
    df = pd.read_csv("wfo.csv", index_col=None, skipinitialspace=True)
    df["utc_valid"] = pd.to_datetime(df["utc_valid"])
    # df["wfo"] = df["wfo"].apply(lambda x: x[1:])
    df = df.set_index("wfo")
    print(df)
    # df["count"] = 100. - df["count"]
    # data = (df["count"] - df["avg"]).round(0).astype(int)
    # data = (df["rank"]).round(0).astype(int)
    vals = df["count"]
    print(vals["PSR"])
    bins = list(range(1, 31, 3))
    # bins = np.arange(2012, 2022, 1)
    # bins = [0, 0.1, 0.2, 0.5, 0.75, 1, 2, 5, 10]
    # bins = [1, 5, 10, 25, 50, 75, 100, 125]
    # bins = np.arange(-3.1, 3.1, 0.5)
    cmap = get_cmap("jet")
    # cmap.set_over("lightyellow")
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        twitter=True,
        title=(
            "2005-2021 Maximum Number of Simultaneous SVR + TOR + FFW + SMW "
            "Warnings"
        ),
        subtitle=(
            "based on unofficial IEM archives up till 19 June 2021"
            # f"nationwide depature {data.sum():.0f} warnings"
            # f"rank of 1 is least number"
        ),
    )
    mp.fill_cwas(
        vals,
        bins=bins,
        lblformat="%.0f",
        # labels=labels,
        labelbuffer=0,
        cmap=cmap,
        ilabel=True,
        # clevlabels=clevlabels,
        units="count",
        extend="neither",
        spacing="proportional",
    )

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
