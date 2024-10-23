"""Apply a bias correction to the ERA5 hourly files."""

import logging
import os
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

    # compute the affine for PRISM
    nc = ncopen("/mesonet/data/prism/1981_daily.nc")
    ncaffine = Affine(
        nc.variables["lon"][1] - nc.variables["lon"][0],
        0.0,
        nc.variables["lon"][0],
        0.0,
        nc.variables["lat"][0] - nc.variables["lat"][1],
        nc.variables["lat"][-1],
    )
    nc.close()
    czs = CachingZonalStats(ncaffine)
    years = range(1981, 2021)
    hucs = df["name"].values
    for year in tqdm(years, total=len(years)):
        df[f"precip_{year}"] = 0
        ncfn = f"/mesonet/data/prism/{year}_daily.nc"
        if not os.path.isfile(ncfn):
            continue
        with ncopen(ncfn) as nc:
            precip = np.nansum(nc.variables["ppt"], 1)
            mypr = czs.gen_stats(np.flipud(precip), df["geometry"])
            df[f"precip_{year}"] = mypr

    print(df["precip_1981"].describe())

    for huc12 in tqdm(hucs):
        hucdf = df[df["name"] == huc12]
        fn = f"precipitation/P{huc12}.txt"
        if not os.path.isfile(fn):
            continue
        era5 = pd.read_csv(fn, skiprows=1, names=["precip"])
        era5["valid"] = pd.date_range(
            "1981/01/01", "2020/12/31 17:00", freq="h"
        )
        era5 = era5.set_index("valid")
        yearly = era5.resample("YE").sum()
        yearly["prism"] = 0
        for year in range(1981, 2021):
            yearly.at[pd.Timestamp(year, 12, 31), "prism"] = hucdf.iloc[0][
                f"precip_{year}"
            ]
        yearly["multiplier"] = yearly["prism"] / yearly["precip"]
        # constrain multiplier to 0.75 and 1.25
        yearly["multiplier"] = np.where(
            yearly["multiplier"] < 0.75, 1, yearly["multiplier"]
        )
        yearly["multiplier"] = np.where(
            yearly["multiplier"] > 1.25, 1, yearly["multiplier"]
        )
        yearly["year"] = yearly.index.year
        yearly = yearly.set_index("year")
        era5["multiplier"] = era5.index.year.map(yearly["multiplier"])
        with open(f"precipitation2/P{huc12}.txt", "w") as fh:
            fh.write("19810101, 60, precipitation\n")
            for _idx, row in era5.iterrows():
                fh.write(f"{row['precip'] * row['multiplier']:.1f}\n")


if __name__ == "__main__":
    main()
