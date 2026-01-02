"""Create and populate the Yearly PRISM climatology netCDF."""

from datetime import datetime
from pathlib import Path

import numpy as np
import rasterio
from pyiem.grid.nav import get_nav
from pyiem.util import logger, ncopen

LOG = logger()
BASEDIR = Path("/mesonet/data/prism")


def populate_file():
    """
    Load up the TIFF files
    """
    fn = BASEDIR / "prism_yearlyc.nc"
    nc = ncopen(fn, "a")
    for varname in ["ppt", "tmax", "tmin"]:
        tiff_fn = BASEDIR / f"prism_{varname}_us_30s_2020_avg_30y.tif"
        with rasterio.open(tiff_fn) as src:
            # raster is top down, netcdf is bottom up
            data = np.flipud(src.read(1))
            # values of -9999 are nodata
            data = np.ma.masked_array(
                data, mask=(data < -9000), fill_value=np.nan
            )
            LOG.info(
                "%s min: %s max: %s",
                varname,
                np.nanmin(data),
                np.nanmax(data),
            )
        nc.variables[varname, :, :] = data

    nc.close()


def init_file():
    """
    Create a new NetCDF file.
    """

    fn = BASEDIR / "prism_yearlyc.nc"
    if fn.exists():
        LOG.info("%s exists, skipping creation...", fn)
        return
    prism_nav = get_nav("PRISM")
    nc = ncopen(fn, "w")
    nc.title = "PRISM Yearly Climatology"
    nc.platform = "Grided Climatology"
    nc.description = "PRISM"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"  # *cough*
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{datetime.now():%d %B %Y} Generated"
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", prism_nav.ny)
    nc.createDimension("lon", prism_nav.nx)
    nc.createDimension("bnds", 2)

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.bounds = "lat_bnds"
    lat.axis = "Y"
    # Grid centers
    lat[:] = prism_nav.y_points

    lat_bnds = nc.createVariable("lat_bnds", float, ("lat", "bnds"))
    lat_bnds[:, 0] = prism_nav.y_edges[:-1]
    lat_bnds[:, 1] = prism_nav.y_edges[1:]

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.bounds = "lon_bnds"
    lon.axis = "X"
    lon[:] = prism_nav.x_points

    lon_bnds = nc.createVariable("lon_bnds", float, ("lon", "bnds"))
    lon_bnds[:, 0] = prism_nav.x_edges[:-1]
    lon_bnds[:, 1] = prism_nav.x_edges[1:]

    # Note the reduced resolution than daily data, max value is ~6200 in prism
    p01d = nc.createVariable(
        "ppt", np.ushort, ("lat", "lon"), fill_value=65535
    )
    # ~6553.5 (cutting it very close!)
    p01d.scale_factor = 0.1
    p01d.add_offset = 0.0
    p01d.units = "mm"
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the year"

    high = nc.createVariable("tmax", np.uint8, ("lat", "lon"), fill_value=255)
    high.scale_factor = 0.5
    high.add_offset = -60.0
    high.units = "C"
    high.long_name = "2m Air Temperature Yearly High"
    high.standard_name = "2m Air Temperature"
    high.coordinates = "lon lat"

    low = nc.createVariable("tmin", np.uint8, ("lat", "lon"), fill_value=255)
    low.scale_factor = 0.5
    low.add_offset = -60.0
    low.units = "C"
    low.long_name = "2m Air Temperature Yearly Low"
    low.standard_name = "2m Air Temperature"
    low.coordinates = "lon lat"

    nc.close()


def main():
    """Go Main"""
    init_file()
    populate_file()


if __name__ == "__main__":
    main()
