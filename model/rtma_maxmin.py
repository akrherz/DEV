"""Figure out the grid max/min values"""
from __future__ import print_function
import os
import datetime

from metpy.units import units
import numpy as np
import pygrib
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot


def plot():
    """Do plotting work"""
    cmap = plt.get_cmap("inferno_r")
    # cmap.set_under('black')
    # cmap.set_over('red')
    minval = (np.load("minval.npy") * units.degK).to(units.degF)
    maxval = (np.load("maxval.npy") * units.degK).to(units.degF)
    diff = maxval - minval
    lons = np.load("lons.npy")
    lats = np.load("lats.npy")
    mp = MapPlot(
        sector="conus",
        title=(
            r"Difference between warmest 3 Oct and coldest 4 "
            "Oct 2m Temperature"
        ),
        subtitle=(
            "based on hourly NCEP Real-Time Mesoscale Analysis "
            "(RTMA) ending midnight CDT"
        ),
    )
    mp.ax.text(
        0.5,
        0.97,
        (
            r"Pixel Difference Range: %.1f$^\circ$F to %.1f$^\circ$F, "
            r"Domain Analysis Range: %.1f$^\circ$F to %.1f$^\circ$F"
        )
        % (
            np.min(diff).magnitude,
            np.max(diff).magnitude,
            np.min(minval).magnitude,
            np.max(maxval).magnitude,
        ),
        transform=mp.ax.transAxes,
        fontsize=12,
        ha="center",
        bbox=dict(pad=0, color="white"),
        zorder=50,
    )
    mp.pcolormesh(
        lons,
        lats,
        diff,
        range(0, 61, 5),
        cmap=cmap,
        clip_on=False,
        units=r"$^\circ$F",
    )
    mp.postprocess(filename="test.png")


def process():
    """Go Main Go"""
    now = datetime.datetime(2018, 10, 4, 6)
    ets = datetime.datetime(2018, 10, 5, 6)
    interval = datetime.timedelta(hours=1)
    minval = None
    maxval = None
    while now < ets:
        fn = now.strftime(
            (
                "/mesonet/ARCHIVE/data/%Y/%m/%d/"
                "model/rtma/%H/rtma.t%Hz.awp2p5f000.grib2"
            )
        )
        if not os.path.isfile(fn):
            print("missing %s" % (fn,))
        else:
            grbs = None
            try:
                grbs = pygrib.open(fn)
                res = grbs.select(shortName="2t")[0].values
                if minval is None:
                    minval = res
                    maxval = res
                    lats, lons = grbs.select(shortName="2t")[0].latlons()
                    np.save("lons", lons)
                    np.save("lats", lats)
                minval = np.where(res < minval, res, minval)
                maxval = np.where(res > maxval, res, maxval)
                print(
                    "%s min: %.1f max: %.1f"
                    % (now, np.min(minval), np.max(maxval))
                )
            except Exception as exp:
                print(fn)
                print(exp)
            finally:
                if grbs:
                    grbs.close()

        now += interval

    # np.save('maxval', maxval)
    np.save("minval", minval)


if __name__ == "__main__":
    # process()
    plot()
