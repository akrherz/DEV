"""Generate PSIMs Tiles.

Run from RUN_NOON.sh for the previous UTC date."""
import datetime
import os

import numpy as np

from pyiem import iemre
from pyiem.datatypes import temperature
from pyiem.meteorology import gdd
from pyiem.util import ncopen, utc


def make_netcdf(fullpath, valid, west, south):
    """Make our netcdf"""
    if os.path.isfile(fullpath):
        return ncopen(fullpath, "a"), False
    nc = ncopen(fullpath, "w")
    # Dimensions
    totaldays = (
        valid.replace(month=12, day=31)
        - valid.replace(year=1980, month=1, day=1)
    ).days + 1
    nc.createDimension("time", totaldays)
    nc.createDimension("lat", 16)  # 0.125 grid over 2 degrees
    nc.createDimension("lon", 16)
    # Coordinate Dimensions
    time = nc.createVariable("time", np.int, ("time",))
    time.units = "days since 1980-01-01 00:00:00"
    time[:] = np.arange(0, totaldays)

    lat = nc.createVariable("lat", np.float, ("lat"))
    lat.units = "degrees_north"
    lat.long_name = "latitude"
    lat[:] = np.arange(south + 0.125 / 2.0, south + 2.0, 0.125)

    lon = nc.createVariable("lon", np.float, ("lon"))
    lon.units = "degrees_east"
    lon.long_name = "longitude"
    lon[:] = np.arange(west + 0.125 / 2.0, west + 2.0, 0.125)

    prcp = nc.createVariable(
        "prcp", np.float, ("time", "lat", "lon"), fill_value=1e20
    )
    prcp.units = "mm/day"
    prcp.long_name = "daily total precipitation"

    tmax = nc.createVariable(
        "tmax", np.float, ("time", "lat", "lon"), fill_value=1e20
    )
    tmax.units = "degrees C"
    tmax.long_name = "daily maximum temperature"

    tmin = nc.createVariable(
        "tmin", np.float, ("time", "lat", "lon"), fill_value=1e20
    )
    tmin.units = "degrees C"
    tmin.long_name = "daily minimum temperature"

    gddf = nc.createVariable(
        "gdd_f", np.float, ("time", "lat", "lon"), fill_value=1e20
    )
    gddf.units = "degrees F"
    gddf.long_name = "Growing Degree Days F (base 50 ceiling 86)"

    srad = nc.createVariable(
        "srad", np.float, ("time", "lat", "lon"), fill_value=1e20
    )
    srad.units = "MJ"
    srad.long_name = "daylight average incident shortwave radiation"

    # did not do vp or cropland
    nc.close()
    nc = ncopen(fullpath, "a")
    return nc, True


def tile_extraction(nc, valid, west, south, isnewfile):
    """Do our tile extraction"""
    # update model metadata
    i, j = iemre.find_ij(west, south)
    islice = slice(i, i + 16)
    jslice = slice(j, j + 16)
    for year in range(1980, 2019):
        tidx0 = (datetime.date(year, 1, 1) - datetime.date(1980, 1, 1)).days
        tidx1 = (
            datetime.date(year + 1, 1, 1) - datetime.date(1980, 1, 1)
        ).days
        tslice = slice(tidx0, tidx1)
        ncfn = iemre.get_daily_ncname(year)
        if not os.path.isfile(ncfn):
            continue
        renc = ncopen(ncfn)
        # print("tslice: %s jslice: %s islice: %s" % (tslice, jslice, islice))
        highc = temperature(
            renc.variables["high_tmpk"][:, jslice, islice], "K"
        ).value("C")
        lowc = temperature(
            renc.variables["low_tmpk"][:, jslice, islice], "K"
        ).value("C")
        nc.variables["tmax"][tslice, :, :] = highc
        nc.variables["tmin"][tslice, :, :] = lowc
        nc.variables["gdd_f"][tslice, :, :] = gdd(
            temperature(highc, "C"), temperature(lowc, "C")
        )
        nc.variables["prcp"][tslice, :, :] = renc.variables["p01d"][
            :, jslice, islice
        ]
        # IEMRE power_swdn is MJ, test to see if data exists
        srad = renc.variables["power_swdn"][:, jslice, islice]
        if srad.mask.all():
            # IEMRE rsds uses W m-2, we want MJ
            srad = (
                renc.variables["rsds"][:, jslice, islice] * 86400.0 / 1000000.0
            )
        nc.variables["srad"][tslice, :, :] = srad

        renc.close()


def workflow(valid, ncfn, west, south):
    """Make the magic happen"""
    basedir = "/mesonet/share/pickup/yieldfx/baseline"
    if not os.path.isdir(basedir):
        os.makedirs(basedir)
    nc, isnewfile = make_netcdf("%s/%s" % (basedir, ncfn), valid, west, south)
    tile_extraction(nc, valid, west, south, isnewfile)
    nc.close()


def main():
    """Go Main Go"""
    # Run for the 12z file yesterday
    today = datetime.date.today() - datetime.timedelta(days=1)
    for hour in [
        0,
    ]:
        valid = utc(today.year, today.month, today.day, hour)
        # Create tiles to cover IA, IL, IN
        for west in np.arange(-98, -84, 2):
            for south in np.arange(36, 44, 2):
                # psims divides its data up into 2x2-degree tiles,
                # with the first number in the file name being number
                # of tiles since 90 degrees north, and the second number
                # being number of tiles since -180 degrees eas
                ncfn = "clim_%04i_%04i.tile.nc4" % (
                    (90 - south) / 2,
                    (180 - (0 - west)) / 2 + 1,
                )
                workflow(valid, ncfn, west, south)


if __name__ == "__main__":
    main()
