"""Create a plot of precip rate frequency per stage IV."""

import numpy as np
from pyiem.iemre import find_ij, get_hourly_ncname
from pyiem.plot import MapPlot, get_cmap, pretty_bins
from pyiem.util import ncopen
from tqdm import tqdm


def plot():
    """Actually plot things."""
    # 1997-2021 (25 years)
    hits = np.load("hits.npy") / 25.0
    mp = MapPlot(
        sector="midwest",
        title="Events per year with 24 hour precipitation >= 50mm",
        subtitle=(
            "Based on PRISM corrected hourly NCEP Stage IV analyses "
            "(1997-2021)"
        ),
        logo="dep",
        caption="Daily Erosion Project",
    )
    xaxis = np.arange(-104, -74, 0.125)
    yaxis = np.arange(35, 49, 0.125)
    xx, yy = np.meshgrid(xaxis, yaxis)
    cmap = get_cmap("terrain_r")
    cmap.set_under("#EEEEEE")
    levels = pretty_bins(0, 4, 10)  # np.max(hits))
    mp.contourf(
        xx,
        yy,
        hits,
        levels,
        iline=False,
        cmap=cmap,
        extend="min",
        units=r"$y^{-1}$",
    )
    mp.fig.savefig("test.png")


def p24():
    """Go Main Go."""
    ll = find_ij(-104, 35)
    ur = find_ij(-74, 49)
    jslice = slice(ll[1], ur[1])
    islice = slice(ll[0], ur[0])
    hits = np.ma.zeros((ur[1] - ll[1], ur[0] - ll[0]))
    progress = tqdm(range(1997, 2022))
    for year in progress:
        progress.set_description(f"{year}")
        lidx = np.ma.zeros((ur[1] - ll[1], ur[0] - ll[0]))
        with ncopen(get_hourly_ncname(year)) as nc:
            p01m = nc.variables["p01m"]
            for tidx in range(24, nc.dimensions["time"].size):
                tslice = slice(tidx - 24, tidx)
                precip = np.ma.sum(p01m[tslice, jslice, islice], axis=0)
                # Prevent double counting
                hits = np.ma.where(
                    np.ma.logical_and(precip >= 50, lidx <= (tidx - 24)),
                    hits + 1,
                    hits,
                )
                lidx = np.ma.where(precip >= 50, tidx, lidx)
    np.save("hits.npy", np.ma.getdata(hits))


def main():
    """Go Main Go."""
    ll = find_ij(-104, 35)
    ur = find_ij(-74, 49)
    jslice = slice(ll[1], ur[1])
    islice = slice(ll[0], ur[0])
    hits = np.ma.zeros((ur[1] - ll[1], ur[0] - ll[0]))
    progress = tqdm(range(1997, 2022))
    for year in progress:
        progress.set_description(f"{year}")
        with ncopen(get_hourly_ncname(year)) as nc:
            p01m = nc.variables["p01m"]
            for tidx in range(nc.dimensions["time"].size):
                hits = np.ma.where(
                    p01m[tidx, jslice, islice] >= 25, hits + 1, hits
                )
    np.save("hits.npy", np.ma.getdata(hits))


if __name__ == "__main__":
    # p24()
    plot()
