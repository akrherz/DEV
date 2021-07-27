"""UGC/Polygon WWA stats onimbus"""
import datetime

import psycopg2.extras
import numpy as np
import pytz
from rasterstats import zonal_stats
import pandas as pd
from geopandas import read_postgis
from affine import Affine
from pyiem.nws import vtec
from pyiem.reference import state_names, state_bounds, wfo_bounds
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn


def do_polygon(ctx):
    """polygon workflow"""
    pgconn = get_dbconn("postgis")
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
    df = read_postgis(
        """
    WITH data as (
        SELECT ST_Forcerhr(ST_Buffer(geom, 0.0005)) as geom,
        rank() OVER (
            PARTITION by wfo, eventid, extract(year from updated)
            ORDER by updated)
        from sbw where phenomena = 'FF' and is_emergency
    ) select * from data where rank = 1
    """,
        pgconn,
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
    for i, z in enumerate(zs):
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

    m = MapPlot(
        title="2009-2019 Flash Flood Emergency Polygon Heatmap",
        sector="custom",
        axisbg="white",
        west=-107,
        south=25.5,
        east=-88,
        north=41,
        # west=-82, south=36., east=-68, north=48,
        # west=-85, south=31.8, north=45.2, east=-69,
        subtitle="based on unofficial IEM Archives",
        nocaption=True,
    )
    cmap = plt.get_cmap("jet")
    cmap.set_under("white")
    cmap.set_over("black")
    res = m.pcolormesh(
        ctx["lons"],
        ctx["lats"],
        ctx["data"],
        ctx["bins"],
        cmap=cmap,
        units="count",
    )
    # Cut down on SVG et al size
    res.set_rasterized(True)

    m.postprocess(filename="test.png")


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
