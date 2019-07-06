"""Copy IEMRE data to the database."""
import sys
import datetime

from tqdm import tqdm
from pyiem.util import ncopen, utc
from pyiem import iemre


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    table = argv[2]
    nc = ncopen("/mesonet/data/iemre/%s_iemre_%s.nc" % (year, table))
    ncvars = {}
    for vname in nc.variables.keys():
        if vname in ['lat', 'lon', 'time', 'hasdata']:
            continue
        ncvars[vname] = nc.variables[vname]

    multi = 24 if table == 'daily' else 1
    for tstep in tqdm(nc.variables['time'][:]):
        ts = utc(year, 1, 1) + datetime.timedelta(hours=int(tstep) * multi)
        ds = iemre.get_grids(ts if table == 'hourly' else ts.date())
        for vname in ncvars:
            ds[vname].values = ncvars[vname][tstep]
        iemre.set_grids(ts if table == 'hourly' else ts.date(), ds)


if __name__ == '__main__':
    main(sys.argv)
