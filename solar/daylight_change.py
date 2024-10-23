"""Cruft."""

import ephem
import netCDF4
import numpy as np
from pyiem import iemre
from pyiem.plot import MapPlot

sun = ephem.Sun()

nc = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")
w = nc.variables["domain"][:]


def do(lat, lon):
    loc = ephem.Observer()
    loc.lat = str(lat)
    loc.long = str(lon)
    loc.date = "2013/06/21"

    rise1 = loc.next_rising(sun).datetime()
    loc.date = "2013/06/22"
    set1 = loc.next_setting(sun).datetime()
    rise2 = loc.next_rising(sun).datetime()
    loc.date = "2013/06/23"
    set2 = loc.next_setting(sun).datetime()

    day1 = (set1 - rise1).seconds + (set1 - rise1).microseconds / 1000000.0
    day2 = (set2 - rise2).seconds + (set2 - rise2).microseconds / 1000000.0
    return day1 - day2


def main():
    """Go Main Go."""
    xs, ys = np.meshgrid(
        np.concatenate([iemre.XAXIS, [iemre.XAXIS[-1] + 0.25]]),
        np.concatenate([iemre.YAXIS, [iemre.YAXIS[-1] + 0.25]]),
    )

    secs = np.zeros(np.shape(w), "f")

    for i, lon in enumerate(iemre.XAXIS):
        for j, lat in enumerate(iemre.YAXIS):
            secs[j, i] = do(lat, lon)

    mp = MapPlot(
        sector="midwest",
        title="21 Jun to 22 Jun 2013 Decrease in Daylight Time",
        subtitle="No local topography considered",
    )

    mp.contourf(
        iemre.XAXIS,
        iemre.YAXIS,
        secs,
        np.arange(2, 6.1, 0.25),
        units="seconds",
    )

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
