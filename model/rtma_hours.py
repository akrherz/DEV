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
    cmap1 = plt.get_cmap("inferno_r")
    colors = list(cmap1(np.arange(10) / 10.0))
    cmap2 = plt.get_cmap("Pastel1")
    colors.extend(list(cmap2(np.arange(2) / 2.0)))
    cmap = ListedColormap(colors)

    cmap.set_under("tan")
    cmap.set_over("white")
    hours = np.load("hours.npy")
    lons = np.load("lons.npy")
    lats = np.load("lats.npy")
    mp = MapPlot(
        sector="midwest",
        statebordercolor="white",
        title=(r"May Total Hours below 32$^\circ$F Air Temperature"),
        subtitle=(
            "based on hourly NCEP Real-Time Mesoscale Analysis "
            "(RTMA) ending 4 AM 12 May 2020 CDT"
        ),
    )

    levels = [1, 4, 8]
    levels2 = list(range(10, 101, 10))
    levels.extend(levels2)
    mp.pcolormesh(
        lons,
        lats,
        hours,
        levels,
        cmap=cmap,
        clip_on=False,
        units="hours",
        spacing="proportional",
        extend="max",
    )
    mp.postprocess(filename="test.png")


def process():
    """Go Main Go"""
    now = datetime.datetime(2020, 5, 1, 5)
    ets = datetime.datetime(2020, 5, 12, 13)
    interval = datetime.timedelta(hours=1)
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
                if hours is None:
                    hours = np.zeros(np.shape(t2))
                    lats, lons = grbs.select(shortName="2t")[0].latlons()
                    np.save("lons", lons)
                    np.save("lats", lats)
            t2 = (t2 * units("degK")).to(units("degF")).magnitude
            hours = np.where(t2 < 32, hours + 1, hours)
            print(f"{now} min: {np.min(hours):.1f} max: {np.max(hours):.1f}")

        now += interval

    np.save("hours", hours)


if __name__ == "__main__":
    # process()
    plot()
