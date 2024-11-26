"""A one off."""

import matplotlib.patheffects as PathEffects
import numpy as np
import pygrib
from matplotlib.patches import Polygon
from pyiem.plot import MapPlot


def main():
    """Go Main Go."""
    m = MapPlot(
        "ames",
        title="Des Moines One Hour Stage IV Precipitation Estimate",
        subtitle="Valid: 26 Jun 2010 12:00 AM CDT",
    )

    m.map.readshapefile("high", "roads", ax=m.ax, drawbounds=False)
    for nshape, seg in enumerate(m.map.roads):
        if (
            m.map.roads_info[nshape]["US1"] in (69, 30)
            or m.map.roads_info[nshape]["INT1"] == 35
        ):
            data = np.array(seg)
            m.ax.plot(
                data[:, 0],
                data[:, 1],
                lw=2,
                linestyle="--",
                color="k",
                zorder=3,
            )

    m.map.readshapefile("cities", "cities", ax=m.ax)
    for nshape, seg in enumerate(m.map.cities):
        if m.map.cities_info[nshape]["NAME10"] != "Ames":
            continue
        poly = Polygon(seg, fc="None", ec="k", lw=1.5, zorder=3)
        m.ax.add_patch(poly)

    grbs = pygrib.open("ST4.2010062605.01h.grib")
    g = grbs.message(1)
    data = g["values"] / 25.4
    lats, lons = g.latlons()

    n1p = [
        0,
        0.01,
        0.1,
        0.3,
        0.5,
        0.8,
        1.0,
        1.3,
        1.5,
        1.8,
        2.0,
        2.5,
        3.0,
        4.0,
        6.0,
        8.0,
    ]
    m.pcolormesh(lons, lats, data, n1p, latlon=True)
    for lo, la, val in zip(
        lons[
            np.logical_and(
                np.logical_and(
                    np.logical_and(lats > 41.965, lats < 42.085), lons > -93.7
                ),
                lons < -93.55,
            )
        ],
        lats[
            np.logical_and(
                np.logical_and(
                    np.logical_and(lats > 41.965, lats < 42.085), lons > -93.7
                ),
                lons < -93.55,
            )
        ],
        data[
            np.logical_and(
                np.logical_and(
                    np.logical_and(lats > 41.965, lats < 42.085), lons > -93.7
                ),
                lons < -93.55,
            )
        ],
        strict=False,
    ):
        xx, yy = m.map(lo + 0.02, la + 0.02)
        txt = m.ax.text(
            xx,
            yy,
            "%.2f" % (val,),
            zorder=5,
            ha="center",
            va="center",
            fontsize=20,
        )
        txt.set_path_effects(
            [PathEffects.withStroke(linewidth=2, foreground="w")]
        )

    m.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
