"""Fix an off-by-one debacle."""

import numpy as np
from pyiem.grid.nav import get_nav
from pyiem.util import logger, ncopen

LOG = logger()


def main():
    """Go Main Go."""
    prism = get_nav("PRISM", "")
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
                prism.bottom + np.arange(prism.ny) * prism.dy
            )
            nc.variables["lat_bnds"][:, 0] = (
                prism.bottom_edge + np.arange(prism.ny) * prism.dy
            )
            nc.variables["lat_bnds"][:, 1] = (
                prism.bottom_edge + np.arange(1, prism.ny + 1) * prism.dy
            )

            nc.variables["lon"][:] = (
                prism.left + np.arange(prism.nx) * prism.dx
            )
            nc.variables["lon_bnds"][:, 0] = (
                prism.left_edge + np.arange(prism.nx) * prism.dx
            )
            nc.variables["lon_bnds"][:, 1] = (
                prism.left_edge + np.arange(1, prism.nx + 1) * prism.dx
            )


if __name__ == "__main__":
    main()
