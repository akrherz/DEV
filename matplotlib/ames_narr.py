import netCDF4
import numpy as np

import matplotlib.patheffects as PathEffects
from matplotlib.patches import Polygon
from pyiem.plot import MapPlot

m = MapPlot(
    "ames",
    title="NARR 3 Hour Total Precipitation",
    subtitle="Valid: 25 Jun 2010 10 PM to 26 Jun 2010 1 AM CDT",
)

m.map.readshapefile("high", "roads", ax=m.ax, drawbounds=False)
for nshape, seg in enumerate(m.map.roads):
    if (
        m.map.roads_info[nshape]["US1"] in (69, 30)
        or m.map.roads_info[nshape]["INT1"] == 35
    ):
        data = np.array(seg)
        m.ax.plot(
            data[:, 0], data[:, 1], lw=2, linestyle="--", color="k", zorder=3
        )

m.map.readshapefile("cities", "cities", ax=m.ax)
for nshape, seg in enumerate(m.map.cities):
    if m.map.cities_info[nshape]["NAME10"] != "Ames":
        continue
    poly = Polygon(seg, fc="None", ec="k", lw=1.5, zorder=3)
    m.ax.add_patch(poly)

nc = netCDF4.Dataset("narr-a_221_20100626_0300_000.grb.nc")

lats = nc.variables["lat"][:]
lons = nc.variables["lon"][:]
pcpn = nc.variables["Total_precipitation"][0, :, :] / 24.5
mask = lons > -100.0
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
m.pcolormesh(lons, lats, pcpn, n1p, latlon=True)

xx, yy = m.map(-93.62, 41.99)
txt = m.ax.text(
    xx, yy, "%.2f" % (0.19,), zorder=5, ha="center", va="center", fontsize=20
)
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])


m.postprocess(filename="test.png")
