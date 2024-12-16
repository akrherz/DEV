"""Fix an off-by-one debacle."""

import numpy as np
from pyiem import prism
from pyiem.util import logger, ncopen

LOG = logger()


def main():
    """Go Main Go."""
    for year in range(1981, 2025):
        LOG.info(year)
        with ncopen(f"/mesonet/data/prism/{year}_daily.nc", "a") as nc:
            nc.createDimension("bnds", 2)
            nc.variables["lat"].bounds = "lat_bnds"
            nc.variables["lon"].bounds = "lon_bnds"
            nc.createVariable("lat_bnds", float, ("lat", "bnds"))
            nc.createVariable("lon_bnds", float, ("lon", "bnds"))
        with ncopen(f"/mesonet/data/prism/{year}_daily.nc", "a") as nc:
            nc.variables["lat"][:] = (
                prism.SOUTH + np.arange(prism.NY) * prism.DY
            )
            nc.variables["lat_bnds"][:, 0] = (
                prism.SOUTH_EDGE + np.arange(prism.NY) * prism.DY
            )
            nc.variables["lat_bnds"][:, 1] = (
                prism.SOUTH_EDGE + np.arange(1, prism.NY + 1) * prism.DY
            )

            nc.variables["lon"][:] = (
                prism.WEST + np.arange(prism.NX) * prism.DX
            )
            nc.variables["lon_bnds"][:, 0] = (
                prism.WEST_EDGE + np.arange(prism.NX) * prism.DX
            )
            nc.variables["lon_bnds"][:, 1] = (
                prism.WEST_EDGE + np.arange(1, prism.NX + 1) * prism.DX
            )


if __name__ == "__main__":
    main()
