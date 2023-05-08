"""Plot things.

https://www.ncei.noaa.gov/data/nclimgrid-monthly/access/
"""

import numpy as np
import xarray as xr

from pyiem.plot import MapPlot, get_cmap
from pyiem.util import c2f


def main():
    """Go."""
    with xr.open_dataset("nclimgrid_tmax.nc") as ds:
        p1 = (
            ds.sel(time=slice("1901-01-01", "1990-12-01"))
            .groupby("time.month")
            .mean("time")
            .sel(month=[7, 8])
            .mean("month")
        )
        p2 = (
            ds.sel(time=slice("1991-01-01", "2020-12-01"))
            .groupby("time.month")
            .mean("time")
            .sel(month=[7, 8])
            .mean("month")
        )
    print(p2)
    mp = MapPlot(
        title="NCEI Climgrid 1991-2020 July-August Change in Ave Daily High",
        subtitle="1991-2020 minus 1901-1990",
        sector="midwest",
        nologo=True,
    )
    lons, lats = np.meshgrid(p2.lon.values, p2.lat.values)
    cmap = get_cmap("RdBu_r")
    cmap.set_bad("#FFFFFF")
    data = c2f(p2.tmax) - c2f(p1.tmax)
    # data.mask = (data < 0.5)
    mp.pcolormesh(
        lons,
        lats,
        data,
        np.arange(-4, 4.1, 1),
        cmap=cmap,
        extend="neither",
        units="F",
    )
    mp.fig.savefig("tmax_delta_ja.png")


if __name__ == "__main__":
    main()
