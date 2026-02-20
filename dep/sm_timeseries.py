"""Plot a time-series with plastic_limit."""

import numpy as np
import pandas as pd
from dailyerosion.io.dep import read_wb
from pyiem.plot import figure_axes


def main():
    """Go Main Go."""
    df = read_wb("/tmp/070802070602_73.wb")
    df = df[df["ofe"] == 1]

    fig, ax = figure_axes(
        title=(
            "Daily Erosion Project\n"
            "Example South Fork Watershed Hillslope 0-10 cm Soil Moisture"
        ),
        logo=None,
        figsize=(8, 6),
    )
    for year in [2012, 2018]:
        sts = pd.Timestamp(year=year, month=1, day=1)
        ets = pd.Timestamp(year=year, month=12, day=31)
        df2 = df[(df["date"] >= sts) & (df["date"] <= ets)].copy()
        ax.plot(
            np.arange(1, len(df2.index) + 1),
            df2["sw1"].values,
            label=f"{year}",
        )
    ax.set_ylim(10, 50)
    ax.set_ylabel("Volumetric Soil Moisture [%]")
    ax.grid(True)
    ax.legend()
    fig.savefig("dep_sm_timeseries.eps")


if __name__ == "__main__":
    main()
