"""Plot WPC"""
from __future__ import print_function
import glob

import pygrib
import numpy as np
import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt
from pyiem.plot import MapPlot
from pyiem import reference
from pyiem.datatypes import distance


def main():
    """Go Main"""
    total = None
    for fn in glob.glob("/tmp/p168m_2018051100f168.grb"):
        grbs = pygrib.open(fn)
        grb = grbs[1]
        if total is None:
            total = grb["values"]
            lats, lons = grb.latlons()
        else:
            total += grb["values"]

    mp = MapPlot(
        sector="custom",
        project="aea",
        south=reference.MW_SOUTH - 5,
        north=reference.MW_NORTH,
        east=reference.MW_EAST,
        west=reference.MW_WEST - 8,
        axisbg="tan",
        title=(
            "Weather Prediction Center (WPC) "
            "Seven Day Quantitative Precip Forecast"
        ),
        subtitle="Falling between 7 PM 10 May and 7 PM 17 May 2018",
    )
    cmap = plt.get_cmap("gist_ncar")
    # cmap.set_bad('tan')
    cmap.set_under("white")
    # cmap.set_over('red')
    levs = np.arange(0, 3.6, 0.25)
    levs[0] = 0.01
    mp.pcolormesh(lons, lats, total / 25.4, levs, cmap=cmap, units="inch")
    mp.draw_usdm(filled=False, hatched=True)

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
