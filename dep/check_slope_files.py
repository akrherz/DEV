"""Review how much minute slopes we have."""

import glob
import os

import numpy as np
from tqdm import tqdm

import matplotlib.colors as mpcolors
import pandas as pd
from cartopy import crs as ccrs
from geopandas import read_postgis
from matplotlib.patches import Polygon
from pyiem.dep import read_slp
from pyiem.plot.geoplot import MapPlot
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def plot():
    """Plot."""
    df2 = pd.read_csv("/tmp/data.csv", dtype={"huc12": str}).set_index("huc12")
    df2["ratio"] = df2["count"] / df2["flowpaths"] * 100.0
    print(df2)
    pgconn = get_dbconn("idep")
    df = read_postgis(
        """
        SELECT huc_12, ST_Transform(simple_geom, 4326) as geom
        from huc12  WHERE scenario = 0
    """,
        pgconn,
        geom_col="geom",
        index_col="huc_12",
    )
    minx, miny, maxx, maxy = df["geom"].total_bounds
    mp = MapPlot(
        title="Percentage of HUC12 Flowpaths with 1+ segments slope < 0.3%",
        subtitle="Overall: %.0f/%.0f (%.2f%%) [Before KS Update]"
        % (
            df2["count"].sum(),
            df2["flowpaths"].sum(),
            df2["count"].sum() / df2["flowpaths"].sum() * 100.0,
        ),
        axisbg="#EEEEEE",
        logo="dep",
        sector="custom",
        south=miny,
        north=maxy,
        west=minx,
        east=maxx,
        projection=ccrs.PlateCarree(),
        nocaption=True,
    )
    cmap = plt.get_cmap("tab20c")
    clevs = np.arange(0, 21.0, 1.0)
    norm = mpcolors.BoundaryNorm(clevs, cmap.N)
    for huc_12, row in df.iterrows():
        val = df2.at[huc_12, "ratio"]
        c = cmap(norm([val]))[0]
        p = Polygon(row["geom"].exterior, fc=c, ec=c, zorder=2, lw=0.1)
        mp.ax.add_patch(p)
    mp.draw_colorbar(clevs, cmap, norm)
    mp.postprocess(filename="test.png")


def dump_data():
    """Generate a file."""
    os.chdir("/mnt/idep2/2/0/slp")
    data = {"huc12": [], "count": [], "flowpaths": []}
    for huc8 in tqdm(glob.glob("*")):
        os.chdir(huc8)
        for huc4 in glob.glob("*"):
            os.chdir(huc4)
            count = 0
            slpfns = glob.glob("*.slp")
            for slpfn in slpfns:
                res = read_slp(slpfn)
                for ofe in res:
                    if np.max(ofe["slopes"]) < 0.003:
                        count += 1
                        break
            data["huc12"].append(huc8 + huc4)
            data["count"].append(count)
            data["flowpaths"].append(len(slpfns))
            os.chdir("..")
        os.chdir("..")
    df = pd.DataFrame(data)
    df.to_csv("/tmp/data.csv", index=False)


def main():
    """Go Main."""
    # dump_data()
    plot()


if __name__ == "__main__":
    main()
