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
        # p1 = (
        #    ds.sel(time=slice("1901-01-01", "1990-12-01"))
        #    .groupby("time.month")
        #    .mean("time")
        #    .sel(month=[7, 8])
        #    .sum("month")
        # )
        p2 = (
            ds.sel(time=slice("1991-01-01", "2020-12-01"))
            .groupby("time.month")
            .mean("time")
            .sel(month=[4, 5, 6])
            .sum("month")
        )
    print(p2)
    mp = MapPlot(
        title="NCEI Climgrid 1991-2020 April-June Precipitation [inch]",
        # subtitle="1991-2020 minus 1901-1990",
        sector="midwest",
        nologo=True,
    )
    lons, lats = np.meshgrid(p2.lon.values, p2.lat.values)
    cmap = get_cmap("viridis_r")
    cmap.set_bad("#FFFFFF")
    data = np.ma.masked_array(mm2inch(p2.prcp))
    data.mask = data < 0.5
    mp.pcolormesh(
        lons,
        lats,
        data,
        np.arange(4, 17.1, 2),
        cmap=cmap,
        extend="neither",
        units="inch",
    )
    mp.fig.savefig("1991_2020_amj.png")


if __name__ == "__main__":
    main()
