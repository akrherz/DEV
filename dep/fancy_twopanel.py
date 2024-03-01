"""playing."""

import numpy as np

import cartopy.crs as ccrs
import matplotlib.colors as mpcolors
from geopandas import read_postgis
from matplotlib.patches import Polygon
from pyiem.dep import RAMPS
from pyiem.plot import geoplot
from pyiem.plot.colormaps import dep_erosion, james
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn

pgconn = get_dbconn("idep")
df = read_postgis(
    """
WITH data as (
SELECT huc_12, avg_delivery * 4.463 as delivery,
qc_precip / 25.4 as precip from results_by_huc12
WHERE scenario = 0 and valid = '2019-5-24')

SELECT ST_Transform(simple_geom, 3857) as geom,
coalesce(d.delivery, 0) as delivery,
coalesce(d.precip, 0) as precip
from huc12 i LEFT JOIN data d
ON (i.huc_12 = d.huc_12) WHERE i.scenario = 0
""",
    pgconn,
    geom_col="geom",
)
minx, miny, maxx, maxy = df["geom"].total_bounds
projection = ccrs.Mercator()
buf = 1000.0
pts = ccrs.Geodetic().transform_points(
    projection,
    np.asarray([minx - buf, maxx + buf]),
    np.asarray([miny - buf, maxy + buf]),
)

fig = plt.figure(figsize=(10.24, 7.68))

cbar_width = 0.018
panel_width = 0.408
geoplot.MAIN_AX_BOUNDS = [0.01, 0.05, panel_width, 0.85]
geoplot.CAX_BOUNDS = [0.01 + panel_width + 0.005, 0.05, cbar_width, 0.85]

cmap = james()
mp = geoplot.MapPlot(
    axisbg="#EEEEEE",
    logo="dep",
    sector="custom",
    south=pts[0, 1],
    north=pts[1, 1],
    west=pts[0, 0],
    east=pts[1, 0],
    projection=projection,
    fig=fig,
    nocaption=True,
)
bins = RAMPS["english"][0]
norm = mpcolors.BoundaryNorm(bins, cmap.N)
for _, row in df.iterrows():
    p = Polygon(
        row["geom"].exterior,
        fc=cmap(norm([row["precip"]]))[0],
        ec="k",
        zorder=2,
        lw=0.1,
    )
    mp.ax.add_patch(p)
lbl = [round(_, 2) for _ in bins]
mp.draw_colorbar(bins, cmap, norm, clevlabels=lbl, spacing="uniform")
mp.ax.text(
    0.5,
    1.01,
    "Total Precipitation [inch]",
    transform=mp.ax.transAxes,
    ha="center",
    fontsize=16,
)
mp.ax.text(
    0.7,
    1.08,
    "Daily Erosion Project May 24, 2019",
    transform=mp.ax.transAxes,
    fontsize=20,
    ha="center",
    va="center",
)

geoplot.MAIN_AX_BOUNDS = [0.51, 0.05, panel_width, 0.85]
geoplot.CAX_BOUNDS = [0.51 + panel_width + 0.005, 0.05, cbar_width, 0.85]

cmap = dep_erosion()
mp = geoplot.MapPlot(
    axisbg="#EEEEEE",
    nologo=True,
    sector="custom",
    south=pts[0, 1],
    north=pts[1, 1],
    west=pts[0, 0],
    east=pts[1, 0],
    nocaption=True,
    projection=projection,
    fig=fig,
)
bins = RAMPS["english"][0]
norm = mpcolors.BoundaryNorm(bins, cmap.N)
for _, row in df.iterrows():
    p = Polygon(
        row["geom"].exterior,
        fc=cmap(norm([row["delivery"]]))[0],
        ec="k",
        zorder=2,
        lw=0.1,
    )
    mp.ax.add_patch(p)
lbl = [round(_, 2) for _ in bins]
mp.draw_colorbar(bins, cmap, norm, clevlabels=lbl, spacing="uniform")
mp.ax.text(
    0.5,
    1.01,
    "Hill Slope Soil Loss [tons/acre]",
    transform=mp.ax.transAxes,
    fontsize=16,
    ha="center",
)


fig.savefig("test.png")
