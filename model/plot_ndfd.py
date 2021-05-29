"""Plot NDFD data.

https://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/VP.001-003/
"""
import datetime

import numpy as np
from pandas.io.sql import read_sql
from pyiem.util import c2f, get_dbconn
from pyiem.plot import MapPlot, get_cmap
import pygrib


def main():
    """Go Main"""
    grbs = pygrib.open("ds.mint.bin")
    # skip 1-off first field
    total = None
    lats = lons = None
    for grb in grbs[1:]:
        if lats is None:
            lats, lons = grb.latlons()
            total = grb["values"]
            continue
        total = c2f(grb["values"] - 273.15)
        print(np.max(total))
        print(grb.validDate)
    # TODO tz-hack here
    analtime = grb.analDate - datetime.timedelta(hours=6)

    mp = MapPlot(
        sector="iowa",
        twitter=True,
        west=-100,
        east=-88,
        north=45,
        south=38,
        axisbg="tan",
        title="NWS 29 May 2021 Morning Low Temperature Forecast",
        subtitle="NDFD Forecast Issued %s, Actual ASOS/AWOS Lows Plotted"
        % (analtime.strftime("%-I %p %-d %B %Y"),),
    )
    cmap = get_cmap("jet")
    bins = np.arange(32, 43, 1)
    mp.pcolormesh(
        lons,
        lats,
        total,
        bins,
        spacing="proportional",
        cmap=cmap,
        units="Fahrenheit",
        clip_on=False,
    )
    df = read_sql(
        "SELECT ST_x(geom) as lon, ST_y(geom) as lat, id, min_tmpf from "
        "summary_2021 s JOIN stations t on (s.iemid = t.iemid) WHERE "
        "s.day = '2021-05-29' and network in ('IA_ASOS', 'AWOS') and "
        "min_tmpf > 0 ORDER by min_tmpf ASC",
        get_dbconn("iem"),
    )
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["min_tmpf"].values,
        labels=df["id"].values,
        fmt="%.0f",
        labelbuffer=2,
    )
    mp.drawcounties()
    # mp.drawcities()
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
