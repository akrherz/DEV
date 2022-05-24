"""Figure out the grid max/min values"""
import os
import datetime

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
import pygrib
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.plot.util import sector_setter, stretch_cmap
from pyiem.reference import Z_FILL, LATLON, EPSG
from pyiem.util import get_sqlalchemy_conn
from scipy import stats
from metpy.units import units


def plot():
    """Do plotting work"""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            "select id, st_x(geom) as lon, st_y(geom) as lat, min_tmpf from "
            "summary_2022 s JOIN stations t on (s.iemid = t.iemid) "
            "WHERE t.network = 'IA_ASOS' and day = '2022-05-23' and "
            "min_tmpf > 0",
            conn,
            index_col="id",
        )
    df["rtma"] = np.nan
    cmap = plt.get_cmap("turbo")
    # cmap.set_under('black')
    # cmap.set_over('red')
    minval = (np.load("minval.npy") * units.degK).to(units.degF).m
    # maxval = (np.load("maxval.npy") * units.degK).to(units.degF)
    # diff = maxval - minval
    lons = np.load("lons.npy")
    lats = np.load("lats.npy")
    for i, row in df.iterrows():
        # find closest point in the rtma grid
        dist = np.sqrt((lons - row["lon"]) ** 2 + (lats - row["lat"]) ** 2)
        (xidx, yidx) = np.unravel_index(dist.argmin(), dist.shape)
        df.loc[i, "rtma"] = minval[xidx, yidx]
    mp = MapPlot(
        sector="iowa",
        title=("Iowa 23 May 2022 Morning Minimum Temperature"),
        subtitle=(
            "analysis based on hourly NCEP Real-Time Mesoscale Analysis "
            "(RTMA), Iowa Airport Observations Overlaid"
        ),
    )
    ax = mp.fig.add_axes([0.05, 0.35, 0.29, 0.3])
    df["delta"] = df["rtma"] - df["min_tmpf"]
    ax.scatter(df["min_tmpf"], df["delta"])
    # Add a fit line
    slope, intercept, _r_value, _p_value, _std_err = stats.linregress(
        df["min_tmpf"], df["delta"]
    )
    ax.plot(
        [32, 50],
        [slope * x + intercept for x in [32, 50]],
        color="red",
        linewidth=2,
    )
    ax.grid(True)
    ax.set_xlabel("Observed Min Temp (F)")
    ax.set_ylabel("RTMA Min Temp Bias (F)", labelpad=3)
    ax.set_title("RTMA Min Temp Bias vs Obs")
    mp.panels[0].ax.set_position([0.35, 0.5, 0.55, 0.4])
    clevs = range(30, 49, 2)
    mp.pcolormesh(
        lons,
        lats,
        minval,
        clevs,
        cmap=cmap,
        clip_on=False,
        units=r"$^\circ$F",
    )
    mp.plot_values(
        df["lon"],
        df["lat"],
        df["min_tmpf"].values,
        fmt="%.0f",
        fontsize=10,
        color="white",
        labelbuffer=0,
        outlinecolor="k",
    )

    mp.fig.text(
        0.4,
        0.46,
        "With Temperature Dependent Bias Correction",
        fontsize=14,
    )
    sector_setter(mp, [0.35, 0.05, 0.55, 0.4])
    cmap = stretch_cmap(cmap, clevs, extend="both")
    norm = mpcolors.BoundaryNorm(clevs, cmap.N)
    mp.panels[1].pcolormesh(
        lons,
        lats,
        minval - (slope * minval) - intercept,
        norm=norm,
        cmap=cmap,
        zorder=Z_FILL,
        crs=LATLON,
    )
    print(mp.panels[0].set_extent(mp.panels[1].get_extent(), EPSG[3857]))
    mp.drawcounties()
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
