"""Figure out the grid max/min values"""
import os
import datetime

import numpy as np
import pygrib
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from metpy.units import units
from metpy.calc import windchill
from matplotlib.colors import ListedColormap


def plot():
    """Do plotting work"""
    cmap1 = plt.get_cmap("inferno_r")
    colors = list(cmap1(np.arange(10) / 10.0))
    cmap2 = plt.get_cmap("Pastel1")
    colors.extend(list(cmap2(np.arange(2) / 2.0)))
    cmap = ListedColormap(colors)

    cmap.set_under("tan")
    cmap.set_over("white")
    minval = np.load("minval.npy")
    maxval = np.load("maxval.npy")
    diff = maxval - minval
    lons = np.load("lons.npy")
    lats = np.load("lats.npy")
    mp = MapPlot(
        sector="midwest",
        statebordercolor="white",
        title=(
            r"Diff between coldest wind chill and warmest "
            "air temp 29 Jan - 3 Feb 2019"
        ),
        subtitle=(
            "based on hourly NCEP Real-Time Mesoscale Analysis "
            "(RTMA) ending midnight CST"
        ),
    )

    levels = list(range(0, 101, 10))
    levels.extend([105, 110])
    mp.pcolormesh(
        lons,
        lats,
        diff,
        levels,
        cmap=cmap,
        clip_on=False,
        units=r"$^\circ$F",
        spacing="proportional",
    )
    mp.postprocess(filename="test.png")


def process():
    """Go Main Go"""
    now = datetime.datetime(2019, 1, 29, 6)
    ets = datetime.datetime(2019, 2, 4, 6)
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
            grbs = pygrib.open(fn)
            try:
                t2 = grbs.select(shortName="2t")[0].values
                u10 = grbs.select(shortName="10u")[0].values
                v10 = grbs.select(shortName="10v")[0].values
            except Exception:
                print("FAIL!")
                now += interval
                continue
            smps = (u10**2 + v10**2) ** 0.5
            wcht = windchill(
                t2 * units("degK"), smps * units("meter / second")
            )
            wcht = wcht.to(units("degF")).magnitude
            t2 = (t2 * units("degK")).to(units("degF")).magnitude
            if minval is None:
                minval = wcht
                maxval = (t2 * units("degK")).to(units("degF")).magnitude
                lats, lons = grbs.select(shortName="2t")[0].latlons()
                np.save("lons", lons)
                np.save("lats", lats)
            minval = np.where(wcht < minval, wcht, minval)
            maxval = np.where(t2 > maxval, t2, maxval)
            print(
                "%s min: %.1f max: %.1f maxdel: %.1f"
                % (
                    now,
                    np.min(minval),
                    np.max(maxval),
                    np.max(maxval - minval),
                )
            )
            grbs.close()

        now += interval

    np.save("maxval", maxval)
    np.save("minval", minval)


if __name__ == "__main__":
    # process()
    plot()
