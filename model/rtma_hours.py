"""Figure out the grid max/min values"""

import datetime
import os

import numpy as np
import pygrib

# from matplotlib.colors import ListedColormap
from metpy.units import units
from pyiem.plot import MapPlot
from pyiem.plot.use_agg import plt


def plot():
    """Do plotting work"""
    cmap = plt.get_cmap("RdBu_r")
    # colors = list(cmap1(np.arange(1, 7) / 7.0))
    # cmap2 = plt.get_cmap("Pastel1")
    # colors.extend(list(cmap2(np.arange(3) / 3.0)))
    # cmap = ListedColormap(colors)

    total = None
    for year in range(2018, 2023):
        val = np.load(f"hours{year}.npy")
        if total is None:
            total = val
        else:
            total += val

    cmap.set_over("yellow")
    cmap.set_under("black")
    hours = np.load("hours.npy") - (total / 5.0)
    hours = np.where(hours == 0, np.nan, hours)
    lons = np.load("lons.npy")
    lats = np.load("lats.npy")
    mp = MapPlot(
        sector="southernplains",
        # south=24,
        # west=-120,
        # north=49,
        # east=-62,
        continentalcolor="white",
        # statebordercolor="white",
        title=(r"2023 Hours AOA 95$^\circ$F Departure from 2018-2022 Average"),
        subtitle=(
            "1 Jan - 5 Sept, based on hourly NCEP Real-Time Mesoscale Analysis"
        ),
    )

    levels = [-350, -200, -100, -50, 0, 50, 100, 200, 350]
    # levels2 = list(range(24, 14 * 24 + 1, 48))
    # levels.extend(levels2)
    # levels = range(12, 145, 12)
    # levels = list(range(0, 14 * 24, 24))
    # levels[0] = 1
    mp.pcolormesh(
        lons,
        lats,
        hours,
        levels,
        cmap=cmap,
        clip_on=False,
        units="hours",
        # spacing="proportional",
        extend="both",
    )
    # mp.drawcounties()
    # mp.draw_usdm(filled=False, hatched=True)
    mp.postprocess(filename="230906.png")


def process():
    """Go Main Go"""
    now = datetime.datetime(2022, 9, 28, 0)
    ets = datetime.datetime(2022, 9, 28, 18)
    interval = datetime.timedelta(hours=1)
    minval = None
    hours = None
    while now < ets:
        fn = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/"
            "model/rtma/%H/rtma.t%Hz.awp2p5f000.grib2"
        )
        if not os.path.isfile(fn):
            print(f"missing {fn}")
        else:
            with pygrib.open(fn) as grbs:
                try:
                    t2 = grbs.select(shortName="2t")[0].values
                except Exception:
                    print(f"failed to get 2t in {fn}!")
                    now += interval
                    continue
                if minval is None:
                    hours = np.zeros(np.shape(t2))
                    minval = np.ones(np.shape(t2)) * 100.0
                    lats, lons = grbs.select(shortName="2t")[0].latlons()
                    np.save("/tmp/lons", lons)
                    np.save("/tmp/lats", lats)
            t2 = (t2 * units("degK")).to(units("degF")).magnitude
            hours = np.where(t2 < 32, hours + 1, hours)
            minval = np.where(t2 < minval, t2, minval)
            print(f"{now} max: {np.max(hours):.1f}")

        now += interval

    np.save("/tmp/hours", hours)
    np.save("/tmp/minval", minval)


if __name__ == "__main__":
    # process()
    plot()
