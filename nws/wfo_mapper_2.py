"""Generic plotter"""

import matplotlib.pyplot as plt
import pandas as pd
from pyiem.plot import MapPlot


def main():
    """Go MAin"""
    df = pd.read_csv("tornado_emergencies.csv")
    df2 = df[
        ["source", "eventid", "phenomena", "significance", "year"]
    ].drop_duplicates()
    gdf = df2.groupby("source").count()
    vals = {}
    labels = {}
    for wfo, row in gdf.iterrows():
        if wfo == "TJSJ":
            wfo = "SJU"
        else:
            wfo = wfo[1:]
        vals[wfo] = int(row["eventid"])
        labels[wfo] = "%s" % (row["eventid"],)

    bins = list(range(0, 31, 3))
    bins[0] = 1
    cmap = plt.get_cmap("plasma_r")
    cmap.set_over("black")
    cmap.set_under("white")
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        figsize=(12.0, 9.0),
        title=("2005-2018 Tornado Emergency Events"),
        subtitle=(
            "based on unofficial IEM archives, searching "
            '"TOR", "SVS". Thru 16 May 2018'
        ),
    )
    mp.fill_cwas(
        vals,
        bins=bins,
        lblformat="%s",
        labels=labels,
        cmap=cmap,
        ilabel=True,  # clevlabels=month_abbr[1:],
        units="count",
    )
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
