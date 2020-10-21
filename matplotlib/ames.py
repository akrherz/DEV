"""A one off."""

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from pyiem import reference
from matplotlib.patches import Polygon
import numpy as np
import pygrib
import Image
from pyiem.plot import MapPlot
import matplotlib.patheffects as PathEffects


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

    """
    img = Image.open('DMX_N1P_201006260459.png')
    data = np.copy( np.asarray(img) )
    data = data.astype(np.float32)


    n1p = [0,0.01,0.1,0.3,0.5,0.8,1.0,1.3,1.5,1.8,2.0,2.5,3.0,4.0,6.0,8.0]
    for i,v in enumerate(n1p):
    data[data==i] = v
    #ntp = [0,0.01,0.3,0.6,1.0,1.5,2.0,2.5,3.0,4.0,5.0,6.0,8.0,10.0,12.0,15.0]
    #for i,v in enumerate(ntp):
    #  data[data==i] = v

    lons1x = np.arange(-96.615703, -96.615703 + 0.005785*1000.0, 0.005785)
    lats1x = np.arange(44.623703, 44.623703 -  0.005785*1000.0, - 0.005785)

    lons, lats = np.meshgrid( lons1x, lats1x)
    res = m.pcolormesh(lons, lats, data, n1p, latlon=True, units='inch')

    ys = np.digitize([41.965,42.085], lats1x)
    xs = np.digitize([-93.7,-93.55], lons1x)
    for x in range(xs[0], xs[1], 3):
        for y in range(ys[1], ys[0], 3):
            xx, yy = m.map(lons1x[x] + 0.0025, lats1x[y] - 0.0025)
            txt = m.ax.text(xx, yy, "%s" % (data[y,x],) , zorder=5, ha='center',
                va='center')
            txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])
    """
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
