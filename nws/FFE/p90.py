"""UGC/Polygon WWA stats onimbus"""

import numpy as np
from affine import Affine
from rasterstats import zonal_stats

import geopandas as gpd
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_sqlalchemy_conn


def do_polygon(ctx):
    """polygon workflow"""
    griddelta = 0.02
    west = -134
    north = 49.5
    south = 24.5
    east = -60.1
    lons = np.arange(west, east, griddelta)
    lats = np.arange(south, north, griddelta)
    YSZ = len(lats)
    XSZ = len(lons)
    lons, lats = np.meshgrid(lons, lats)
    affine = Affine(griddelta, 0.0, west, 0.0, 0 - griddelta, north)
    ones = np.ones((int(YSZ), int(XSZ)))
    counts = np.zeros((int(YSZ), int(XSZ)))
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            """
        WITH data as (
            SELECT ST_Forcerhr(ST_Buffer(geom, 0.0005)) as geom,
            rank() OVER (
                PARTITION by wfo, eventid, extract(year from updated)
                ORDER by updated)
            from sbw where phenomena = 'FF' and is_emergency
        ) select * from data where rank = 1
        """,
            conn,
            geom_col="geom",
            index_col=None,
        )
    # print df, sts, ets, west, east, south, north
    zs = zonal_stats(
        df["geom"],
        ones,
        affine=affine,
        nodata=-1,
        all_touched=True,
        raster_out=True,
    )
    for _i, z in enumerate(zs):
        aff = z["mini_raster_affine"]
        mywest = aff.c
        mynorth = aff.f
        raster = np.flipud(z["mini_raster_array"])
        x0 = int((mywest - west) / griddelta)
        y1 = int((mynorth - south) / griddelta)
        dy, dx = np.shape(raster)
        x1 = x0 + dx
        y0 = y1 - dy
        if x0 < 0 or x1 >= XSZ or y0 < 0 or y1 >= YSZ:
            # print raster.mask.shape, west, x0, x1, XSZ, north, y0, y1, YSZ
            continue
        counts[y0:y1, x0:x1] += np.where(raster.mask, 0, 1)

    maxv = np.max(counts)
    if maxv < 8:
        bins = np.arange(1, 8, 1)
    else:
        bins = np.linspace(1, maxv + 3, 10, dtype="i")
    ctx["bins"] = bins
    ctx["data"] = counts
    ctx["lats"] = lats
    ctx["lons"] = lons


def plotter(ctx):
    """Go"""
    # Covert datetime to UTC
    do_polygon(ctx)

    mp = MapPlot(
        title="2009-2022 Flash Flood Emergency Polygon Heatmap",
        sector="state",
        state="TX",
        axisbg="white",
        # west=-107,
        # south=25.5,
        # east=-88,
        # north=41,
        # west=-82, south=36., east=-68, north=48,
        # west=-85, south=31.8, north=45.2, east=-69,
        subtitle="based on unofficial IEM Archives with data till 30 May 2022",
        nocaption=True,
    )
    cmap = get_cmap("jet")
    cmap.set_under("white")
    cmap.set_over("black")
    res = mp.pcolormesh(
        ctx["lons"],
        ctx["lats"],
        ctx["data"],
        ctx["bins"],
        cmap=cmap,
        units="count",
        extend="both",
    )
    mp.drawcounties()
    # Cut down on SVG et al size
    res.set_rasterized(True)

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    plotter(
        dict(
            geo="polygon",
            state="NM",
            phenomena="SV",
            significance="W",
            v="lastyear",
            year=1986,
            year2=2017,
        )
    )
