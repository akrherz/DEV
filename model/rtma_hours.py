"""Figure out the grid max/min values"""
import os
import datetime

from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
import numpy as np
import pygrib
from metpy.units import units
from matplotlib.colors import ListedColormap


def plot():
    """Do plotting work"""
    cmap1 = plt.get_cmap("terrain_r")
    colors = list(cmap1(np.arange(11) / 12.0))
    # cmap2 = plt.get_cmap("Pastel1")
    # colors.extend(list(cmap2(np.arange(3) / 3.0)))
    cmap = ListedColormap(colors)

    # cmap.set_under("tan")
    cmap.set_under("white")
    hours = np.load("/tmp/hours.npy")
    minval = np.load("/tmp/minval.npy")
    lons = np.load("/tmp/lons.npy")
    lats = np.load("/tmp/lats.npy")
    mp = MapPlot(
        sector="custom",
        south=40,
        west=-100,
        north=49,
        east=-87,
        twitter=True,
        continentalcolor="tan",
        # statebordercolor="white",
        title=(
            r"6 PM 27 Sep - 12 PM 28 Sep 2022 :: Hours below 32$^\circ$F Air Temperature"
        ),
        subtitle="based on hourly NCEP Real-Time Mesoscale Analysis",
    )

    # levels = [1, 4, 8, 12]
    # levels2 = list(range(24, 14 * 24 + 1, 48))
    # levels.extend(levels2)
    # levels = range(12, 145, 12)
    levels = range(1, 9)
    mp.pcolormesh(
        lons,
        lats,
        hours,
        levels,
        cmap=cmap,
        clip_on=False,
        units="hours",
        spacing="proportional",
        extend="both",
    )
    mp.drawcounties()
    mp.postprocess(filename="220929.png")


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
