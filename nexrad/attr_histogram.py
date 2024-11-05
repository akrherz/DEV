"""Generates the nice histograms on the IEM website"""

import calendar
import sys

import numpy as np
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.plot import get_cmap
from pyiem.plot.use_agg import plt
from pyiem.util import get_sqlalchemy_conn, utc
from tqdm import tqdm


def run(nexrad, name, network, cname):
    """Do some work!"""
    cmap = get_cmap(cname)
    cmap.set_bad("white")

    today = utc()
    with get_sqlalchemy_conn("radar") as conn:
        df = pd.read_sql(
            "SELECT drct, sknt, extract(doy from valid) as doy, valid "
            "from nexrad_attributes_log WHERE nexrad = %s and sknt > 0",
            conn,
            params=(nexrad,),
            index_col=None,
        )
    if df.empty:
        print(f"No results for {nexrad}")
        return
    minvalid = df["valid"].min()

    years = (today - minvalid).days / 365.25
    fig = plt.figure(figsize=(10.24, 7.68), dpi=100)
    ax = [None, None]
    ax[0] = fig.add_axes([0.06, 0.53, 0.99, 0.39])
    ax[1] = fig.add_axes([0.06, 0.06, 0.99, 0.39])

    H2, xedges, yedges = np.histogram2d(
        df["drct"].values,
        df["sknt"].values,
        bins=(36, 15),
        range=[[0, 360], [0, 70]],
    )
    H2 = np.ma.array(H2 / years)
    H2.mask = np.where(H2 < 1, True, False)
    res = ax[0].pcolormesh(xedges, yedges, H2.transpose(), cmap=cmap)
    fig.colorbar(res, ax=ax[0], extend="neither")
    ax[0].set_xlim(0, 360)
    ax[0].set_ylabel("Storm Speed [kts]")
    ax[0].set_xlabel("Movement Direction (from)")
    ax[0].set_xticks((0, 90, 180, 270, 360))
    ax[0].set_xticklabels(("N", "E", "S", "W", "N"))
    ax[0].set_title(
        "Storm Attributes Histogram\n"
        f"{minvalid:%d %b %Y} - {today:%d %b %Y} K{nexrad} "
        f"{name} ({network})\n"
        f"{len(df.index)} total attrs, units are ~ (attrs+scans)/year"
    )
    ax[0].grid(True)

    H2, xedges, yedges = np.histogram2d(
        df["doy"].values,
        df["drct"].values,
        bins=(36, 36),
        range=[[0, 365], [0, 360]],
    )
    H2 = np.ma.array(H2 / years)
    H2.mask = np.where(H2 < 1, True, False)
    res = ax[1].pcolormesh(xedges, yedges, H2.transpose(), cmap=cmap)
    fig.colorbar(res, ax=ax[1], extend="neither")
    ax[1].set_ylim(0, 360)
    ax[1].set_ylabel("Movement Direction (from)")
    ax[1].set_yticks((0, 90, 180, 270, 360))
    ax[1].set_yticklabels(("N", "E", "S", "W", "N"))
    ax[1].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].set_xlim(0, 365)
    ax[1].grid(True)

    ax[1].set_xlabel(
        f"Generated {today:%-d %b %Y} by Iowa Environmental Mesonet"
    )

    fig.savefig(f"{nexrad}_histogram.png")
    plt.close()


def main(argv):
    """See how we are called"""
    nt = NetworkTable(["NEXRAD", "TWDR"])
    stations = list(nt.sts.keys())
    stations.sort()
    cname = "hot_r"
    if len(argv) > 1:
        stations = [argv[1]]
        cname = argv[2]
    progress = tqdm(stations)
    for sid in progress:
        progress.set_description(sid)
        run(sid, nt.sts[sid]["name"], nt.sts[sid]["network"], cname)


if __name__ == "__main__":
    main(sys.argv)
