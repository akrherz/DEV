"""Plot NDFD data.

https://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/VP.001-003/
"""
import datetime

from pyiem.plot import MapPlot, nwssnow
import pygrib


def main():
    """Go Main"""
    grbs = pygrib.open("ds.snow.bin")
    # skip 1-off first field
    total = None
    lats = lons = None
    for grb in grbs[1:]:
        if lats is None:
            lats, lons = grb.latlons()
            total = grb["values"]
            continue
        total += grb["values"]
        print(grb.validDate)
    # TODO tz-hack here
    analtime = grb.analDate - datetime.timedelta(hours=6)

    mp = MapPlot(
        sector="custom",
        west=-100,
        east=-88,
        north=46,
        south=40,
        axisbg="tan",
        title=(
            "NWS Forecasted Accumulated Snowfall "
            "thru 12 PM 27 November 2019"
        ),
        subtitle="NDFD Forecast Issued %s"
        % (analtime.strftime("%-I %p %-d %B %Y"),),
    )
    cmap = nwssnow()
    cmap.set_bad("tan")
    mp.pcolormesh(
        lons,
        lats,
        total * 39.3701,
        [0.01, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36],
        cmap=cmap,
        units="inch",
    )

    mp.drawcounties()
    mp.drawcities()
    mp.postprocess(filename="test.png")
    mp.close()


if __name__ == "__main__":
    main()
