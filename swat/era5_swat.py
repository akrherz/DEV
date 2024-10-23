"""Process the ERA5Land files for SWAT."""

import logging
from collections import namedtuple

import geopandas as gpd
import numpy as np
import pandas as pd
from affine import Affine
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import logger, ncopen
from tqdm import tqdm

LOG = logger()
LOG.setLevel(logging.INFO)
GRIDINFO = namedtuple("GridInfo", ["x0", "y0", "xsz", "ysz", "mask"])


def main():
    """Go Main Go"""
    dfs = []
    for i in range(1, 4):
        dfs.append(gpd.read_file(f"{i}.json"))
    df = gpd.GeoDataFrame(pd.concat(dfs))

    # compute the affine
    ncaffine = Affine(0.1, 0.0, -126, 0.0, -0.1, 50)
    czs = CachingZonalStats(ncaffine)
    fps = []
    years = range(1981, 2021)
    first_run = True
    hucs = df["name"].values
    for year in tqdm(years, total=len(years)):
        with ncopen(f"/mesonet/data/era5/{year}_era5land_hourly.nc") as nc:
            nc_p01m = nc.variables["p01m"]
            if first_run:
                for j, huc14 in enumerate(hucs):
                    fps.append(
                        [
                            open(
                                f"precipitation/P{huc14}.txt",
                                "w",
                                encoding="ascii",
                            ),
                            open(
                                f"temperature/T{huc14}.txt",
                                "w",
                                encoding="ascii",
                            ),
                        ]
                    )
                    fps[j][0].write("19810101,60,precipitation\n")
                    fps[j][1].write("19810101,60,temperature\n")

            first_run = False
            for i in range(0, nc.variables["time"].shape[0]):
                precip = nc_p01m[i]
                mypr = czs.gen_stats(np.flipud(precip), df["geometry"])
                for j in range(len(fps)):
                    fps[j][0].write(f"{mypr[j]:.1f}\n")

    for fp in fps:
        fp[0].close()
        fp[1].close()


if __name__ == "__main__":
    main()
