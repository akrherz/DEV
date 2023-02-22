"""Plot things.

https://www.ncei.noaa.gov/data/nclimgrid-monthly/access/
"""

import numpy as np
import xarray as xr
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import mm2inch


def main():
    """Go."""
    with xr.open_dataset("nclimgrid_prcp.nc") as ds:
        p1 = (
            ds.sel(time=slice("1901-01-01", "1990-12-01"))
            .groupby("time.month")
            .mean("time")
            .sel(month=[7, 8])
            .sum("month")
        )
        p2 = (
            ds.sel(time=slice("1991-01-01", "2020-12-01"))
            .groupby("time.month")
            .mean("time")
            .sel(month=[7, 8])
            .sum("month")
        )
    print(p1)
    mp = MapPlot(
        title="NCEI Climgrid Change in July-August Precipitation",
        subtitle="1991-2020 minus 1901-1990",
        sector="midwest",
    )
    lons, lats = np.meshgrid(p1.lon.values, p1.lat.values)
    mp.pcolormesh(
        lons,
        lats,
        mm2inch(p2.prcp - p1.prcp),
        np.arange(-2.5, 2.6, 0.5),
        cmap=get_cmap("RdBu"),
        units="inch",
    )
    mp.fig.savefig("delta2.png")


if __name__ == "__main__":
    main()
