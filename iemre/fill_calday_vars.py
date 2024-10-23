"""Copy grids, when there's lots of missing data.

For old dates, we only have 12z totals, so these are copied to the calday
totals.
"""

import numpy as np
from pyiem.iemre import get_daily_ncname
from pyiem.util import ncopen


def main():
    """Go Main Go"""
    for year in range(1893, 2018):
        nc = ncopen(get_daily_ncname(year), "a", timeout=600)
        gridsize = nc.dimensions["lat"].size * nc.dimensions["lon"].size
        for vname in ["p01d", "high_tmpk", "low_tmpk"]:
            for i in range(nc.variables[vname].shape[0]):
                calday = nc.variables[vname][i, :, :]
                # Get a count of missing values
                missing = np.sum(calday.mask) / float(gridsize)
                if missing > 0.5:
                    print("%s_12z->%s %s %.2f" % (vname, vname, i, missing))
                    nc.variables[vname][i, :, :] = nc.variables[
                        vname + "_12z"
                    ][i, :, :]

        nc.close()


if __name__ == "__main__":
    main()
