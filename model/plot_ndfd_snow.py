"""Plot NDFD data.

https://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/VP.001-003/
"""
import datetime

import numpy as np
import pygrib
from pyiem.plot import MapPlot, nwssnow


def main():
    """Go Main"""
    grbs = pygrib.open("/tmp/ds.snow.bin")
    total = None
    lats = lons = None
    # grib ordering starts at 1
    for grb in grbs[1:9]:
        if lats is None:
            lats, lons = grb.latlons()
            total = grb["values"]
            continue
        total += grb["values"] * 1000.0
        print(np.max(total))
        print(grb.validDate)
    # TODO tz-hack here
    analtime = grb.analDate - datetime.timedelta(hours=6)

    mp = MapPlot(
        sector="custom",
        west=-100,
        east=-88,
        north=46.5,
        south=39.5,
        axisbg="tan",
        title="NWS Forecast Accumulated Snowfall thru 12 AM 16 January 2022",
        subtitle=f"NDFD Forecast Issued {analtime:%-I %p %-d %B %Y}",
    )
    cmap = nwssnow()
    bins = [0.1, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36]
    mp.pcolormesh(
        lons,
        lats,
        total / 25.4,
        bins,
        spacing="proportional",
        cmap=cmap,
        units="inch",
        clip_on=False,
    )

    mp.drawcounties()
    mp.drawcities()
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
