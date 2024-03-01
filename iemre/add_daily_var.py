"""Add a variable"""

import os

import numpy as np

from pyiem import iemre
from pyiem.util import ncopen


def main():
    """go Main go"""
    for yr in range(1893, 2024):
        fn = iemre.get_daily_ncname(yr)
        if not os.path.isfile(fn):
            print("Miss %s" % (fn,))
            continue
        print(fn)
        nc = ncopen(fn, "a", timeout=300)
        v1 = nc.createVariable(
            "high_soil4t", np.uint16, ("time", "lat", "lon"), fill_value=65535
        )
        v1.units = "K"
        v1.scale_factor = 0.01
        v1.long_name = "4inch Soil Temperature Daily High"
        v1.standard_name = "4inch Soil Temperature"
        v1.coordinates = "lon lat"

        v1 = nc.createVariable(
            "low_soil4t", np.uint16, ("time", "lat", "lon"), fill_value=65535
        )
        v1.units = "K"
        v1.scale_factor = 0.01
        v1.long_name = "4inch Soil Temperature Daily Low"
        v1.standard_name = "4inch Soil Temperature"
        v1.coordinates = "lon lat"

        nc.sync()
        nc.close()


if __name__ == "__main__":
    main()
