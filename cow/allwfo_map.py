"""Generate a pretty map."""

import numpy as np

import pandas as pd
from pyiem.plot.geoplot import MapPlot
from pyiem.plot.use_agg import plt


def main():
    """Go Main Go."""
    df = pd.read_csv("allwfo.csv", index_col="wfo")
    mp = MapPlot(
        sector="nws",
        title=(
            "Tornado + Svr T'Storm Warning Polygon Shared Border "
            "with County [%]"
        ),
        subtitle=(
            "1 Jan 2019 - 7 May 2024: based on unofficial IEM archives, "
            "no accomodation for CWA border."
        ),
    )
    cmap = plt.get_cmap("jet")
    mp.fill_cwas(
        df["shared_border[%]"],
        bins=np.arange(0, 101, 10),
        cmap=cmap,
        extend="neither",
        ilabel=True,
        lblformat="%.0f",
        labelbuffer=0,
        units="%",
    )
    mp.postprocess(filename="190101_240507_svrtor_shared_perimeter.png")


if __name__ == "__main__":
    main()
