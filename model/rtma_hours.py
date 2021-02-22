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
    cmap1 = plt.get_cmap("nipy_spectral_r")
    colors = list(cmap1(np.arange(13) / 14.0))
    # cmap2 = plt.get_cmap("Pastel1")
    # colors.extend(list(cmap2(np.arange(3) / 3.0)))
    cmap = ListedColormap(colors)

    cmap.set_under("tan")
    cmap.set_over("white")
    hours = np.load("maxhours.npy")
    lons = np.load("lons.npy")
    lats = np.load("lats.npy")
    mp = MapPlot(
        sector="conus",
        south=25,
        west=-121,
        east=-68,
        north=50,
        twitter=True,
        continentalcolor="tan",
        # statebordercolor="white",
        title=(
            r"1 Jan - 22 Feb 2021 Maximum Consecutive Hours below 32$^\circ$F "
            "Air Temperature"
        ),
        subtitle=(
            "based on hourly NCEP Real-Time Mesoscale Analysis "
            "(RTMA) ending 3 PM 22 Feb 2021 CST"
        ),
    )

    # levels = [1, 4, 8, 12]
    # levels2 = list(range(24, 14 * 24 + 1, 48))
    # levels.extend(levels2)
    # levels = range(12, 145, 12)
    levels = [1, 3, 6, 12, 24, 48, 72, 120, 240, 15 * 24, 480, 720, 40 * 24]
    clevlabels = [
        "1hr",
        "3hr",
        "6hr",
        "12hr",
        "1",
        "2",
        3,
        5,
        10,
        15,
        20,
        30,
        40,
    ]
    mp.pcolormesh(
        lons,
        lats,
        hours,
        levels,
        cmap=cmap,
        clip_on=False,
        units="days",
        clevlabels=clevlabels,
        # spacing="proportional",
        extend="both",
    )
    # mp.drawcounties()
    mp.postprocess(filename="test.png")


def process():
    """Go Main Go"""
    now = datetime.datetime(2021, 2, 1, 6)
    ets = datetime.datetime(2021, 2, 19, 2)
    interval = datetime.timedelta(hours=1)
    current = None
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
                if current is None:
                    current = np.zeros(np.shape(t2))
                    maxhours = np.zeros(np.shape(t2))
                    lats, lons = grbs.select(shortName="2t")[0].latlons()
                    np.save("lons", lons)
                    np.save("lats", lats)
            t2 = (t2 * units("degK")).to(units("degF")).magnitude
            current = np.where(t2 < 0, current + 1, 0)
            maxhours = np.where(current > maxhours, current, maxhours)
            print(f"{now} max: {np.max(maxhours):.1f}")

        now += interval

    np.save("maxhours", maxhours)


if __name__ == "__main__":
    # process()
    plot()
