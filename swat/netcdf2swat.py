"""Convert netcdf data to SWAT"""

import datetime
from collections import namedtuple

import geopandas as gpd
import netCDF4
import numpy as np
from affine import Affine
from pyiem.grid.zs import CachingZonalStats
from pyproj import Proj
from tqdm import tqdm

GRIDINFO = namedtuple("GridInfo", ["x0", "y0", "xsz", "ysz", "mask"])
LCC = Proj(
    "+proj=lcc +lon_0=-97. +y_0=0.0 +R=6367470. +x_0=0.0 +units=m +lat_2=60 "
    "+lat_1=35 +lat_0=46"
)


def main():
    """Go Main Go"""
    huc8df = gpd.read_file("huc8.shp")
    hucs = huc8df["HUC8"].values
    years = range(1960, 2100)

    # compute the affine with imagery in top down
    ncaffine = Affine(
        25_000.0,
        0.0,
        25_000.0 * -158,
        0.0,
        -25_000.0,
        25_000.0 * 150,  # northern border
    )
    huc8df_projected = huc8df.to_crs(LCC.crs)
    czs = CachingZonalStats(ncaffine)

    fps = []
    now = datetime.date(1960, 8, 1)
    for year in years:
        # Time storage is ahead in time
        delta = datetime.date(year + 2, 1, 1) - datetime.date(year + 1, 1, 1)
        is_leap_year = delta.days == 366
        precnc = netCDF4.Dataset(
            f"PREC/prec.daily.cesm2-le.1011.bias-correct.d01.{year}.nc"
        )
        tmaxnc = netCDF4.Dataset(
            f"TMAX/t2max.daily.cesm2-le.1011.bias-correct.d01.{year}.nc"
        )
        tminnc = netCDF4.Dataset(
            f"TMIN/t2min.daily.cesm2-le.1011.bias-correct.d01.{year}.nc"
        )
        for i in tqdm(range(365), desc=f"{year}"):
            # flip all arrays north south
            t2max = np.flipud(tmaxnc.variables["t2max"][i]) - 273.15
            t2min = np.flipud(tminnc.variables["t2min"][i]) - 273.15
            pr = np.flipud(precnc.variables["prec"][i])
            myt2max = czs.gen_stats(t2max, huc8df_projected["geometry"])
            myt2min = czs.gen_stats(t2min, huc8df_projected["geometry"])
            mypr = czs.gen_stats(pr, huc8df_projected["geometry"])
            for j, huc8 in enumerate(hucs):
                if i == 0 and year == years[0]:
                    fps.append(
                        [
                            open(
                                f"swat/precipitation/P{huc8}.txt",
                                "w",
                                encoding="utf8",
                            ),
                            open(
                                f"swat/temperature/T{huc8}.txt",
                                "w",
                                encoding="utf8",
                            ),
                        ]
                    )
                    fps[j][0].write("%s\n" % (now.strftime("%Y%m%d"),))
                    fps[j][1].write("%s\n" % (now.strftime("%Y%m%d"),))
                fps[j][0].write(("%.1f\n") % (mypr[j],))
                fps[j][1].write(("%.2f,%.2f\n") % (myt2max[j], myt2min[j]))
                # 1 Aug + days to reach Feb 28 for leap years
                if is_leap_year and i == 213:
                    fps[j][0].write("0.0\n")
                    fps[j][1].write(("%.2f,%.2f\n") % (myt2max[j], myt2min[j]))
        precnc.close()
        tmaxnc.close()
        tminnc.close()
    for fp in fps:
        fp[0].close()
        fp[1].close()


if __name__ == "__main__":
    main()
