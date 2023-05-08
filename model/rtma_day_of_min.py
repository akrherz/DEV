"""Figure out the grid min date."""
# stdlib
import datetime
import os

# third party
import numpy as np
import pygrib

from pyiem.plot import MapPlot
from pyiem.plot.use_agg import plt


def plot():
    """Do plotting work"""
    cmap = plt.get_cmap("nipy_spectral")
    # cmap.set_under('black')
    # cmap.set_over('red')
    days = np.load("days.npy")
    print(np.min(days))
    lons = np.load("lons.npy")
    lats = np.load("lats.npy")
    mp = MapPlot(
        twitter=True,
        sector="conus",
        title=(
            "1 Oct 2020 - 28 Jan 2021 :: Date of Coldest Hourly 2m Air "
            "Temperature"
        ),
        subtitle=(
            "based on hourly NCEP Real-Time Mesoscale Analysis "
            "(RTMA), through 4 AM CST 28 Jan 2021"
        ),
    )
    levels = []
    levellabels = []
    for i in range(-80, 31):
        dt = datetime.datetime(2021, 1, 1) + datetime.timedelta(days=i)
        if dt.day in [8, 18, 28]:
            levels.append(i)
            levellabels.append(dt.strftime("%-d %b"))

    mp.pcolormesh(
        lons,
        lats,
        days,
        levels,
        clevlabels=levellabels,
        cmap=cmap,
        clip_on=False,
        units="Date",
        spacing="proportional",
    )
    mp.postprocess(filename="test.png")


def process():
    """Go Main Go"""
    now = datetime.datetime(2020, 10, 1)
    ets = datetime.datetime(2021, 1, 28, 0)
    interval = datetime.timedelta(hours=1)
    minval = None
    days = None
    # We may be getting bootstraped.
    if os.path.isfile("minval.npy"):
        minval = np.load("minval.npy")
        days = np.load("days.npy")
    while now < ets:
        fn = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/rtma/%H/"
            "rtma.t%Hz.awp2p5f000.grib2"
        )
        if not os.path.isfile(fn):
            pass
            # print("missing %s" % (fn,))
        else:
            grbs = None
            try:
                grbs = pygrib.open(fn)
                res = grbs.select(shortName="2t")[0].values
                if minval is None:
                    minval = res
                    lats, lons = grbs.select(shortName="2t")[0].latlons()
                    np.save("lons", lons)
                    np.save("lats", lats)
                    days = np.zeros(res.shape)
                minval = np.where(res < minval, res, minval)
                offset = (now - datetime.datetime(2021, 1, 1, 6)).days
                days = np.where(res <= minval, offset, days)
                print(
                    "%s min: %.1f hits: %s"
                    % (now, np.min(minval), np.sum(days == offset))
                )
            except Exception as exp:
                print(fn)
                print(exp)
            finally:
                if grbs:
                    grbs.close()

        now += interval

    print(days.dtype)
    print(minval.dtype)
    np.save("days", days)
    np.save("minval", minval)


if __name__ == "__main__":
    # process()
    plot()
