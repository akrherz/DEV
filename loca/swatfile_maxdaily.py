"""Check over our SWAT files for irregularities."""

import datetime
import glob
import os
import sys

import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon
from pyiem.database import get_dbconn
from pyiem.plot.colormaps import stretch_cmap
from pyiem.plot.geoplot import MapPlot
from tqdm import tqdm


def plot(argv):
    """Make a plot"""
    df = pd.read_csv(
        "%s_maxdailyprecip.txt" % (argv[1],), dtype={"huc12": str}
    )
    df.set_index("huc12", inplace=True)
    pgconn = get_dbconn("idep")
    huc12df = gpd.GeoDataFrame.from_postgis(
        """
    SELECT huc12, simple_geom as geo from wbd_huc12
    WHERE swat_use ORDER by huc12
    """,
        pgconn,
        index_col="huc12",
        geom_col="geo",
    )
    mp = MapPlot(
        sector="custom",
        south=34,
        north=48,
        west=-98,
        east=-77,
        title="%s Max Daily Precipitation" % (argv[1].split("_", 1)[1],),
    )
    bins = range(0, 201, 20)
    cmap = stretch_cmap("terrain_r", bins)
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    for huc12, row in huc12df.iterrows():
        for poly in row["geo"]:
            arr = np.asarray(poly.exterior)
            points = mp.ax.projection.transform_points(
                ccrs.Geodetic(), arr[:, 0], arr[:, 1]
            )
            color = cmap(norm([df.at[huc12, "maxp"]]))[0]
            poly = Polygon(
                points[:, :2], fc=color, ec="None", zorder=2, lw=0.1
            )
            mp.ax.add_patch(poly)
    mp.draw_colorbar(bins, cmap, norm, units="mm")
    mp.postprocess(filename="test.png")


def main(argv):
    """Run main Run."""
    mydir = argv[1]
    fp = open("%s_maxdailyprecip.txt" % (mydir,), "w")
    fp.write("huc12,maxp\n")
    os.chdir(mydir)
    os.chdir("precipitation")
    for fn in tqdm(glob.glob("*.txt")):
        df = pd.read_csv(fn)
        sdate = datetime.datetime.strptime(df.columns[0], "%Y%m%d")
        df.columns = ["precip_mm"]
        df["date"] = pd.date_range(sdate, periods=len(df.index))
        df.set_index("date", inplace=True)
        fp.write("%s,%s\n" % (fn[1:-4], df["precip_mm"].max()))
    fp.close()


if __name__ == "__main__":
    # main(sys.argv)
    plot(sys.argv)
