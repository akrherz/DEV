"""Days with threshold based on prism.

Note the massive memory usage here :/
"""

import datetime

import matplotlib.pyplot as plt
import netCDF4
import numpy as np
from pyiem.datatypes import temperature
from pyiem.iemre import daily_offset
from pyiem.plot.geoplot import MapPlot
from tqdm import tqdm

THRESHOLD = temperature(90, "F").value("C")


def main():
    """Go Main"""
    total = None
    years = 0.0
    progress = tqdm(list(range(1981, 2026)))
    for yr in progress:
        progress.set_description(f"Processing {yr}")
        ncfn = f"/mesonet/data/prism/{yr}_daily.nc"
        nc = netCDF4.Dataset(ncfn)
        if total is None:
            lons = nc.variables["lon"][:]
            lats = nc.variables["lat"][:]
            total = np.zeros(nc.variables["tmax"].shape[1:], np.float64)
        sidx = daily_offset(datetime.date(yr, 1, 1))
        eidx = daily_offset(datetime.date(yr, 11, 24))
        # Read all days at once and use vectorized comparison
        tmax = nc.variables["tmax"][sidx:eidx]
        days = np.sum(tmax > THRESHOLD, axis=0).astype(np.float64)
        nc.close()
        years += 1.0
        total += days

    val = days - (total / years)
    print(np.max(val))
    print(np.min(val))
    mp = MapPlot(
        sector="conus",
        title="Oregon State PRISM 2025 Days with High >= 90°F Departure",
        subtitle="2025 thru 23 Nov against 1981-2024 Year to Date Average",
    )
    mp.contourf(
        lons,
        lats,
        val,
        np.arange(-25, 26, 5),
        units="days",
        cmap=plt.get_cmap("seismic"),
    )
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
