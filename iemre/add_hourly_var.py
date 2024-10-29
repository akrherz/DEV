"""Add a variable"""

import os

import numpy as np
from pyiem import iemre
from pyiem.util import ncopen


def main():
    """go Main go"""
    for yr in range(1850, 2025):
        for domain in ["", "china", "europe"]:
            fn = iemre.get_hourly_ncname(yr, domain=domain)
            if not os.path.isfile(fn):
                print(f"Miss {fn}")
                continue
            print(fn)
            nc = ncopen(fn, "a", timeout=300)
            rsds = nc.createVariable(
                "rsds", np.uint16, ("time", "lat", "lon"), fill_value=65535
            )
            rsds.units = "W m-2"
            rsds.scale_factor = 0.03
            rsds.long_name = "Downward Solar Radiation Flux"
            rsds.standard_name = "Downward Solar Radiation Flux at Surface"
            rsds.coordinates = "lon lat"
            nc.sync()
            nc.close()


if __name__ == "__main__":
    main()
