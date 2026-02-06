"""Figure out the grid max/min values"""

import datetime
import os

import numpy as np
import pygrib

# from matplotlib.colors import ListedColormap
from pyiem.plot import MapPlot, get_cmap


def plot():
    """Do plotting work"""
    # cmap = get_cmap("RdBu_r")
    # colors = list(cmap1(np.arange(1, 7) / 7.0))
    cmap = get_cmap("coolwarm_r")
    # colors.extend(list(cmap2(np.arange(3) / 3.0)))
    # cmap = ListedColormap(colors)

    hours = np.load("/tmp/hours.npy") / 24.0

    # cmap.set_over("yellow")
    # cmap.set_under("black")
    hours = np.where(hours == 0, np.nan, hours)
    lons = np.load("/tmp/lons.npy")
    lats = np.load("/tmp/lats.npy")
    mp = MapPlot(
        sector="iowa",
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

    # levels = [-350, -200, -100, -50, 0, 50, 100, 200, 350]
    levels = list(range(0, 25, 2))
    levels[0] = 0.1
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
        units="days",
        # spacing="proportional",
        extend="max",
    )
    # mp.drawcounties()
    # mp.draw_usdm(filled=False, hatched=True)
    mp.postprocess(filename="260206.png")


def process():
    """Go Main Go"""
    now = datetime.datetime(2026, 2, 5, 6)
    ets = datetime.datetime(2026, 1, 1, 0)
    interval = datetime.timedelta(hours=-1)
    hits = None
    hours = None
    while now > ets:
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
                if hits is None:
                    hours = np.zeros(np.shape(t2))
                    hits = np.zeros(np.shape(t2))
                    lats, lons = grbs.select(shortName="2t")[0].latlons()
                    np.save("/tmp/lons", lons)
                    np.save("/tmp/lats", lats)
            hours = np.where(
                np.logical_and(t2 < 273.15, hits == 0), hours + 1, hours
            )
            hits = np.where(t2 > 273.15, 1, hits)
            print(f"{now} max: {np.max(hours):.1f}")

        now += interval

    np.save("/tmp/hours", hours)
    np.save("/tmp/hits", hits)


if __name__ == "__main__":
    # process()
    plot()
