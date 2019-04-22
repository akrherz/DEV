"""Add a variable"""
from __future__ import print_function
import os

import numpy as np
from pyiem import iemre
from pyiem.util import ncopen


def main():
    """go Main go"""
    for yr in range(1893, 2020):
        fn = iemre.get_daily_ncname(yr)
        if not os.path.isfile(fn):
            print("Miss %s" % (fn, ))
            continue
        print(fn)
        nc = ncopen(fn, 'a', timeout=300)
        v1 = nc.createVariable(
            'power_swdn', np.float, ('time', 'lat', 'lon'),
            fill_value=1.e20)
        v1.units = 'MJ d-1'
        v1.long_name = 'All Sky Insolation Incident on a Horizontal Surface'
        v1.standard_name = (
            'All Sky Insolation Incident on a Horizontal Surface'
        )
        v1.coordinates = "lon lat"
        v1.description = "from NASA POWER"

        nc.sync()
        nc.close()


if __name__ == '__main__':
    main()
