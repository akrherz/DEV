"""Plot NARR."""
import numpy as np

from pyiem.datatypes import distance
from pyiem.plot import MapPlot
from pyiem.util import ncopen


def main():
    """Go Main Go"""
    nc = ncopen("/mesonet/data/iemre/1979_narr.nc")

    data = np.sum(nc.variables["apcp"][:, :, :], axis=0)

    m = MapPlot(
        sector="conus", axisbg="tan", title=(""), subtitle="", titlefontsize=16
    )

    t = distance(data, "MM").value("IN")
    m.pcolormesh(
        nc.variables["lon"][:],
        nc.variables["lat"][:],
        t,
        np.arange(0, 60, 2),
        units="F",
    )

    m.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
