"""Dump IEMRE for counties even

Average precipitation by month for the past 5 years over all counties in Iowa
Average 4-inch soil temp by month for the past 5 years over all counties Iowa
Average high/ low temperature for the past 5 years over all counties in Iowa

average daily precipitation, 4" soil temperature and high/low temperature


1950 thru 2017
"""
import datetime

import numpy as np
from affine import Affine
from tqdm import tqdm

import geopandas as gpd
import pandas as pd
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import convert_value, get_sqlalchemy_conn, ncopen


def step2():
    """Build the monthly averages ..."""
    df = pd.read_csv(
        "counties.csv",
        parse_dates=[
            "date",
        ],
    )
    df["precip_in"] = convert_value(df["precip"].values, "millimeter", "inch")
    df["soilt_f"] = convert_value(df["soilt"].values, "degK", "degF")
    df["high_f"] = convert_value(df["high"].values, "degK", "degF")
    df["low_f"] = convert_value(df["low"].values, "degK", "degF")
    df = df.drop(columns=["precip", "soilt", "high", "low"])
    df.groupby(["county", df["date"].dt.month]).mean().to_csv("monthly.csv")


def main():
    """Go Please"""
    with get_sqlalchemy_conn("postgis") as pgconn:
        counties = gpd.GeoDataFrame.from_postgis(
            """
        SELECT simple_geom, name from ugcs where substr(ugc, 1, 3) = 'IAC'
        and end_ts is null
        """,
            pgconn,
            index_col="name",
            geom_col="simple_geom",
        )
    czs = CachingZonalStats(Affine(0.1, 0.0, -126, 0.0, -0.1, 50))

    output = open("counties.csv", "w")
    output.write("county,date,precip,soilt,high,low\n")
    for year in tqdm(range(2019, 2024)):
        nc = ncopen(
            f"/mesonet/data/era5/{year}_era5land_hourly.nc", "r", timeout=300
        )
        for i, tstep in enumerate(range(6, nc.variables["time"].size, 24)):
            date = datetime.date(year, 1, 1) + datetime.timedelta(days=i)
            high = np.ma.max(
                nc.variables["tmpk"][tstep : tstep + 24, :, :], axis=0
            )
            low = np.ma.min(
                nc.variables["tmpk"][tstep : tstep + 24, :, :], axis=0
            )
            pday = np.ma.sum(
                nc.variables["p01m"][tstep : tstep + 24, :, :], axis=0
            )
            soilt = np.ma.mean(
                nc.variables["soilt"][tstep : tstep + 24, 0, :, :], axis=0
            )
            chigh = czs.gen_stats(np.flipud(high), counties["simple_geom"])
            clow = czs.gen_stats(np.flipud(low), counties["simple_geom"])
            cprecip = czs.gen_stats(np.flipud(pday), counties["simple_geom"])
            csoilt = czs.gen_stats(np.flipud(soilt), counties["simple_geom"])
            for i, fips in enumerate(counties.index.values):
                output.write(
                    ("%s,%s,%.2f,%.2f,%.2f,%.2f\n")
                    % (fips, date, cprecip[i], csoilt[i], chigh[i], clow[i])
                )
        nc.close()
    output.close()


if __name__ == "__main__":
    # main()
    step2()
