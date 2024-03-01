"""Process the ERA5Land files for SWAT."""

import sys

import numpy as np

import pandas as pd
from metpy.calc import relative_humidity_from_dewpoint
from metpy.units import units
from pyiem.iemre import hourly_offset
from pyiem.util import logger, ncopen, utc

LOG = logger()


def main(argv):
    """Go Main Go"""
    lon = float(argv[1])
    lat = float(argv[2])
    gridx = None
    gridy = None

    res = []
    for year in range(1950, 2023):
        print(year)
        with ncopen(f"/mesonet/data/era5/{year}_era5land_hourly.nc") as nc:
            if gridx is None:
                gridx = np.digitize(lon, nc.variables["lon"][:])
                gridy = np.digitize(lat, nc.variables["lat"][:])
            tidx0 = hourly_offset(utc(year, int(argv[3]), 1, 5))
            for hour, tidx in enumerate(range(tidx0, tidx0 + 24)):
                tmpk = nc.variables["tmpk"][tidx, gridy, gridx]
                dwpk = nc.variables["dwpk"][tidx, gridy, gridx]
                relh = relative_humidity_from_dewpoint(
                    units("degK") * tmpk,
                    units("degK") * dwpk,
                ).m
                # W/m2 J/m2s
                rsds = nc.variables["rsds"][tidx, gridy, gridx]
                res.append(
                    {
                        "hour": hour,
                        "tmpc": (units("degK") * tmpk).to(units("degC")).m,
                        "relh": relh * 100.0,
                        "rsds": rsds * 3_600 / 1_000_000.0,
                    }
                )
    df = pd.DataFrame(res)
    df.groupby("hour").mean().to_csv("data.csv")


if __name__ == "__main__":
    main(sys.argv)
