"""Period between rainfalls"""

import datetime

import matplotlib.pyplot as plt
import numpy as np
import pytz
from pyiem import iemre, plot
from pyiem.datatypes import distance
from pyiem.util import ncopen

THRESHOLD = distance(0.25, "in").value("mm")


def main():
    """Go Main Go"""
    sts = datetime.datetime(2018, 4, 20, 0)
    sts = sts.replace(tzinfo=pytz.utc)
    ets = datetime.datetime(2018, 5, 11, 0)
    ets = ets.replace(tzinfo=pytz.utc)

    nc = ncopen(iemre.get_hourly_ncname(sts.year))
    lons = nc.variables["lon"][:]
    lats = nc.variables["lat"][:]
    running = np.zeros((len(nc.dimensions["lat"]), len(nc.dimensions["lon"])))
    maxval = np.zeros((len(nc.dimensions["lat"]), len(nc.dimensions["lon"])))
    interval = datetime.timedelta(hours=1)
    now = sts
    i, j = iemre.find_ij(-93.61, 41.99)
    while now < ets:
        offset = iemre.hourly_offset(now)
        p01m = np.sum(nc.variables["p01m"][offset - 24 : offset], axis=0)
        # 0.05in is 1.27 mm
        this = np.where(p01m > THRESHOLD, 1, 0)
        running = np.where(this == 1, 0, running + 1)
        maxval = np.where(running > maxval, running, maxval)
        print("%s %s %s" % (now, running[j, i], maxval[j, i]))

        now += interval

    # maxval = numpy.where(domain == 1, maxval, 1.e20)

    m = plot.MapPlot(
        sector="midwest",
        title="Max Period between 24 Hour 0.25+ inch Total Precipitation",
        subtitle=(
            "Period of 20 Apr - 11 May 2018, based on NCEP Stage IV data"
        ),
    )

    extra = lons[-1] + (lons[-1] - lons[-2])
    lons[-1] = extra
    # lons = np.concatenate([lons, [extra, ]])

    extra = lats[-1] + (lats[-1] - lats[-2])
    lats[-1] = extra
    # lats = np.concatenate([lats, [extra, ]])

    lons, lats = np.meshgrid(lons, lats)
    # m.pcolormesh(x, y, maxval / 24.0, numpy.arange(0,25,1), units='days')
    maxval = np.where(maxval > 800, 73.0, maxval)
    cmap = plt.get_cmap("terrain")
    m.contourf(
        lons,
        lats,
        maxval / 24.0,
        np.arange(1, 11.1, 1),
        cmap=cmap,
        units="days",
        clip_on=False,
    )
    m.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
