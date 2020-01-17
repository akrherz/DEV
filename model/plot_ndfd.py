"""Plot NDFD data.

https://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/VP.001-003/
"""
import datetime

import numpy as np
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot, nwssnow
import pygrib


def main():
    """Go Main"""
    grbs = pygrib.open("ds.iceaccum.bin")
    # skip 1-off first field
    total = None
    lats = lons = None
    for grb in grbs[1:]:
        if lats is None:
            lats, lons = grb.latlons()
            total = grb["values"]
            continue
        total += grb["values"]
        print(np.max(total))
        print(grb.validDate)
    # TODO tz-hack here
    analtime = grb.analDate - datetime.timedelta(hours=6)

    mp = MapPlot(
        sector="iowa",
        west=-100,
        east=-88,
        north=45,
        south=38,
        axisbg="tan",
        title=("NWS Forecast Accumulated Ice " "thru 12 AM 20 January 2020"),
        subtitle="NDFD Forecast Issued %s"
        % (analtime.strftime("%-I %p %-d %B %Y"),),
    )
    cmap = plt.get_cmap("tab20c_r")
    cmap.set_under("white")
    cmap.set_over("red")
    bins = np.arange(0, 0.21, 0.04)
    bins[0] = 0.01
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
    mp.close()


if __name__ == "__main__":
    main()
