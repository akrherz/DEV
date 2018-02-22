"""Oh the hackery and pain here

Back in the day, when an explicit 12z precip field was added to the IEMRE
netcdf files, I renamed the precip variable to calendar day and never copied
it to the 12z field, since for old time data, there is no hope but to have
these as equal.
"""
from __future__ import print_function

import numpy as np
import netCDF4


def main():
    """Go Main Go"""
    for year in range(1893, 2018):
        nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (year, ),
                             'a')
        for i in range(nc.variables['p01d_12z'].shape[0]):
            p01d_12 = nc.variables['p01d_12z'][i, :, :]
            p01d = nc.variables['p01d'][i, :, :]
            if (isinstance(p01d_12, np.ma.MaskedArray) and
                    not isinstance(p01d, np.ma.MaskedArray)):
                print(("%s[%s] copy p01d -> p01d_12z mean: %5.2fmm"
                       ) % (year, i, np.ma.mean(p01d)))
                nc.variables['p01d_12z'][i] = p01d
        nc.close()


if __name__ == '__main__':
    main()
