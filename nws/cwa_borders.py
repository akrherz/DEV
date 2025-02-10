"""Where are the CWA borders at?"""

# third party
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
from tqdm import tqdm


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis")
    nt = NetworkTable("WFO")
    axis = np.arange(-300, 301, 10)
    total = np.zeros((axis.shape[0] - 1, axis.shape[0] - 1))
    for wfo in tqdm(nt.sts):
        if nt.sts[wfo]["state"] in ["PR", "AK", "HI"]:
            continue
        df = pd.read_sql(
            """
        WITH wlocs as (
            select st_x(st_transform(geom, 2163)) as x,
            ST_y(st_transform(geom, 2163)) as y from stations
            where id = %s and network = 'WFO'),
        pts as (
            SELECT st_dumppoints(st_transform(the_geom, 2163)) as g
            from cwa where wfo = %s),
        pts2 as (
            SELECT st_x((g).geom) as x, st_y((g).geom) as y from pts)

        SELECT p.x - w.x as x, p.y - w.y as y from pts2 p, wlocs w
        """,
            pgconn,
            params=(wfo, wfo),
            index_col=None,
        )
        h2d, xedges, yedges = np.histogram2d(
            df["x"].to_numpy() / 1000.0,
            df["y"].to_numpy() / 1000.0,
            list(axis),
        )
        # trick here is just to put any value > 0 as 1
        total += np.where(h2d > 0, 1, 0)

    total = np.ma.array(total)
    total.mask = np.ma.where(total < 1, True, False)
    maxval = np.nanmax(total)
    (fig, ax) = plt.subplots(1, 1)
    ax.set_xlabel("X Distance from WFO [km]")
    ax.set_ylabel("Y Distance from WFO [km]")
    ax.set_title(
        "Frequency of NWS Office's own CWA Border\n"
        "for CONUS NWS Offices, all borders considered (ie coastal)"
    )
    fig.text(0.02, 0.01, "@akrherz 16 Nov 2017")
    fig.text(0.99, 0.01, "computed in US Albers EPSG:2163", ha="right")
    res = ax.pcolormesh(xedges, yedges, total.transpose() / maxval)
    for rng in range(25, 201, 25):
        circle = plt.Circle((0, 0), rng, edgecolor="r", facecolor="None")
        ax.add_artist(circle)
    ax.grid(True)
    fig.colorbar(res, label="Normalized Count (max: %.0f)" % (maxval,))
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
