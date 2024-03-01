"""Days with threshold based on prism"""

import datetime

import netCDF4
import numpy as np

import matplotlib.pyplot as plt
from pyiem.datatypes import temperature
from pyiem.iemre import daily_offset
from pyiem.plot.geoplot import MapPlot

THRESHOLD = temperature(90, "F").value("C")


def main():
    """Go Main"""
    total = None
    years = 0.0
    for yr in range(1981, 2018):
        print(yr)
        ncfn = "/mesonet/data/prism/%s_daily.nc" % (yr,)
        nc = netCDF4.Dataset(ncfn)
        if total is None:
            lons = nc.variables["lon"][:]
            lats = nc.variables["lat"][:]
            total = np.zeros(nc.variables["tmax"].shape[1:], np.float)
        days = np.zeros(nc.variables["tmax"].shape[1:], np.float)
        sidx = daily_offset(datetime.date(yr, 1, 1))
        eidx = daily_offset(datetime.date(yr, 7, 4))
        for idx in range(sidx, eidx):
            days += np.where(nc.variables["tmax"][idx, :, :] > THRESHOLD, 1, 0)
        nc.close()
        years += 1.0
        total += days

    val = days - (total / years)
    print(np.max(val))
    print(np.min(val))
    mp = MapPlot(
        sector="conus",
        title=("OSU PRISM 2017 Days with High >= 90$^\circ$F " "Departure"),
        subtitle=(
            "2017 thru 4 July against 1981-2016 " "Year to Date Average"
        ),
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
