"""Generate a pretty map."""

import numpy as np

import pandas as pd
from pyiem.plot.geoplot import MapPlot
from pyiem.plot.use_agg import plt


def main():
    """Go Main Go."""
    df = pd.read_csv("allwfo.csv", index_col="wfo")
    mp = MapPlot(
        sector="conus",
        title="2015-2019 June-August Severe Thunderstorm Warning POD",
        subtitle=(
            "based on unofficial IEM Cow stats using Local Storm Reports"
        ),
    )
    cmap = plt.get_cmap("plasma")
    mp.fill_cwas(
        df["POD[1]"],
        bins=np.arange(0, 1.01, 0.1),
        cmap=cmap,
        extend="neither",
        ilabel=True,
        lblformat="%.2f",
    )
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
