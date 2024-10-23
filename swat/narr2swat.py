"""Dump NARR data to swat for Alex circa 27 Feb 2023

https://psl.noaa.gov/data/gridded/data.narr.html
"""

import logging
from collections import namedtuple

import geopandas as gpd
import numpy as np
from affine import Affine
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import get_sqlalchemy_conn, logger, ncopen
from sqlalchemy import text
from tqdm import tqdm

LOG = logger()
LOG.setLevel(logging.INFO)
GRIDINFO = namedtuple("GridInfo", ["x0", "y0", "xsz", "ysz", "mask"])
PROJSTR = (
    "+proj=lcc +lat_1=50 +lat_2=50 +lat_0=50 +lon_0=-107. "
    "+a=6370000 +b=6370000 +towgs84=0,0,0 +units=m +no_defs"
)


def main():
    """Go Main Go"""
    with get_sqlalchemy_conn("idep") as conn:
        huc12df = gpd.read_postgis(
            text(
                """
            SELECT huc8, ST_Transform(simple_geom, :prj) as geo from wbd_huc8
            WHERE swat_use ORDER by huc8
        """
            ),
            conn,
            index_col="huc8",
            params={"prj": PROJSTR},
            geom_col="geo",
        )
    hucs = huc12df.index.values

    # compute the affine
    ncaffine = Affine(32463, 0.0, -5632642, 0.0, -32463, 4347243)
    czs = CachingZonalStats(ncaffine)
    fps = []
    years = range(1989, 2011)
    first_run = True
    for year in tqdm(years, total=len(years)):
        apcp = ncopen(f"apcp.{year}.nc")
        t2 = ncopen(f"air.2m.{year}.nc")
        times = apcp.variables["time"].shape[0]
        # 6z to 6z
        x = 2
        while x < times:
            tmax = np.max(t2.variables["air"][x : (x + 8)], 0)
            tmin = np.min(t2.variables["air"][x : (x + 8)], 0)
            precip = np.sum(apcp.variables["apcp"][(x + 1) : (x + 9)], 0)

            mytasmax = czs.gen_stats(np.flipud(tmax), huc12df["geo"])
            mytasmin = czs.gen_stats(np.flipud(tmin), huc12df["geo"])
            mypr = czs.gen_stats(np.flipud(precip), huc12df["geo"])
            for j, huc12 in enumerate(hucs):
                if first_run:
                    fps.append(
                        [
                            open(
                                f"precipitation/P{huc12}.txt",
                                "w",
                                encoding="ascii",
                            ),
                            open(
                                f"temperature/T{huc12}.txt",
                                "w",
                                encoding="ascii",
                            ),
                        ]
                    )
                    fps[j][0].write("19890101\n")
                    fps[j][1].write("19890101\n")

                fps[j][0].write(f"{mypr[j]:.1f}\n")
                fps[j][1].write(
                    f"{mytasmax[j] - 273.15:.2f},{mytasmin[j] - 273.15:.2f}\n"
                )
            first_run = False
            x += 8

    for fp in fps:
        fp[0].close()
        fp[1].close()


if __name__ == "__main__":
    main()
