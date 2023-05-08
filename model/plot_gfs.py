"""Plot GFS."""
import numpy as np
import pygrib

from pyiem.datatypes import temperature
from pyiem.plot import MapPlot, get_cmap


def main():
    """Go Main Go."""
    grbs = pygrib.open("gfs.t00z.sfluxgrbf189.grib2")

    grb = grbs.select(name="2 metre temperature")[0]
    lats, lons = grb.latlons()

    lons = np.where(lons > 180, lons - 360, lons)

    m = MapPlot(
        sector="midwest",
        axisbg="tan",
        title=(
            "NCEP Global Forecast System (GFS) "
            "2m Air Temp valid 3 PM 15 December 2021"
        ),
        subtitle="189 Hour Forecast from 00 UTC run on 8 December 2021",
        titlefontsize=16,
    )

    t = temperature(grb["values"], "K").value("F")
    cmap = get_cmap("turbo")
    m.pcolormesh(
        lons[5:-5, 5:-5],
        lats[5:-5, 5:-5],
        t[5:-5, 5:-5],
        np.arange(25, 76, 5),
        clevlabelstride=5,
        cmap=cmap,
        units="F",
        clip_on=False,
    )

    m.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
