"""Create a netcdf file with an given data point"""

import datetime

import netCDF4
import numpy as np


def main():
    """Do the work"""
    onc = netCDF4.Dataset("dump.nc", "a")
    lat = 41.99044
    lon = -93.61852
    onc.variables["lat"][:] = lat
    onc.variables["lon"][:] = lon
    base = datetime.datetime(1997, 1, 1)

    i = 0
    for year in range(1997, 2018):
        nc = netCDF4.Dataset(
            "/mesonet/data/stage4/" + str(year) + "_stage4_hourly.nc"
        )
        if year == 1997:
            dist = (
                (nc.variables["lon"][:] - lon) ** 2
                + (nc.variables["lat"][:] - lat) ** 2
            ) ** 0.5
            (xidx, yidx) = np.unravel_index(dist.argmin(), dist.shape)

        # mm for hour to kg/m2/s
        data = nc.variables["p01m"][:, yidx, xidx] / 100.0 / 3600.0
        time = nc.variables["time"][:]
        sz = time.shape[0]
        offset = (
            datetime.datetime(year, 1, 1) - base
        ).total_seconds() / 3600.0
        onc.variables["time"][i : i + sz] = time + offset
        onc.variables["pr"][i : i + sz] = data

        nc.close()
        i += sz
    onc.close()


def create_nc():
    """Go Main Go"""
    nc = netCDF4.Dataset("dump.nc", "w")
    nc.createDimension("lat", 1)
    nc.createDimension("lon", 1)
    nc.createDimension("time", None)
    nc.createDimension("bnds", 2)

    lon = nc.createVariable("lon", "d", ("lon"))
    lon.units = "degrees_east"
    lon.long_name = "longitude"
    lon.standard_name = "longitude"
    # lon.actual_range = [-33.8800048828125, 41.3599853515625]

    lat = nc.createVariable("lat", "d", ("lat"))
    lat.units = "degrees_north"
    lat.long_name = "latitude"
    lat.standard_name = "latitude"

    time = nc.createVariable("time", "d", ("time",))
    time.long_name = "time"
    time.standard_name = "time"
    time.axis = "T"
    time.calendar = "365_day"
    time.units = "hours since 1997-01-01 00:00:00"
    time.delta_t = "0000-00-00 00:00:00"
    time.bounds = "time_bnds"
    time.coordinate_defines = "point"
    # time.actual_range = 20471.0208333333, 20835.9791666667 ;

    nc.createVariable("time_bnds", "d", ("time", "bnds"))

    pr = nc.createVariable("pr", "d", ("time", "lat", "lon"), fill_value=1e20)
    pr.units = "kg m-2 s-1"
    pr.missing_value = 1e20
    pr.long_name = "Precipitation"
    pr.standard_name = "precipitation_flux"
    pr.coordinates = "lon lat"
    pr.cell_methods = "time: mean"

    nc.Conventions = "CF-1.4"
    nc.close()


if __name__ == "__main__":
    # create_nc()
    main()
