"""Plot NDFD data.

https://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/VP.001-003/
"""
import datetime

import numpy as np
import pygrib

from pyiem.plot import MapPlot, get_cmap
from pyiem.util import c2f


def main():
    """Go Main"""
    grbs = pygrib.open("/tmp/ds.maxt.bin")
    grb = grbs[3]
    lats, lons = grb.latlons()
    total = c2f(grb["values"] - 273.15)
    print(grb.validDate)
    # TODO tz-hack here
    analtime = grb.analDate - datetime.timedelta(hours=5)

    mp = MapPlot(
        sector="iowa",
        twitter=True,
        west=-100,
        east=-88,
        north=45,
        south=38,
        axisbg="tan",
        title="NWS 3 August 2022 Afternoon High Temperature Forecast",
        subtitle=f"NDFD Forecast Issued {analtime:%-I %p %-d %B %Y}",
    )
    cmap = get_cmap("turbo")
    bins = np.arange(90, 105, 2)
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
    """
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
    """
    mp.drawcounties()
    # mp.drawcities()
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
