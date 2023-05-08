"""Copy IEMRE data to the database.

    Usage: python copy_to_database.py <hourly/daily> <YYYY> <mm> <dd> <HH24>
"""
import sys

from pyiem import iemre
from pyiem.util import ncopen, utc


def main(argv):
    """Go Main Go."""
    table = argv[1]
    valid = utc(int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5]))
    if table == "daily":
        valid = valid.date()
        tidx = iemre.daily_offset(valid)
    else:
        tidx = iemre.hourly_offset(valid)
    ncvars = {}
    with ncopen(
        "/mesonet/data/iemre/%s_iemre_%s.nc" % (valid.year, table)
    ) as nc:
        for vname in nc.variables.keys():
            if vname in ["lat", "lon", "time", "hasdata"]:
                continue
            ncvars[vname] = nc.variables[vname][tidx, :, :]

    ds = iemre.get_grids(valid)
    for vname in ncvars:
        ds[vname].values = ncvars[vname]
    iemre.set_grids(valid, ds)


if __name__ == "__main__":
    main(sys.argv)
