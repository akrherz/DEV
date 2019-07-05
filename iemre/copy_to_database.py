"""Copy IEMRE data to the database."""
import sys
from collections import OrderedDict
import datetime
from io import StringIO

from tqdm import tqdm
from pyiem.util import ncopen, get_dbconn
import pandas as pd


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    table = argv[2]
    if table == 'hourly':
        month = int(argv[3])
        dbtable = "iemre_hourly_%i%02i" % (year, month)
    else:
        dbtable = "iemre_daily_%i" % (year, )
    pgconn = get_dbconn('iemre')
    cursor = pgconn.cursor()
    cursor.execute("TRUNCATE " + dbtable)
    cursor.close()
    pgconn.commit()
    nc = ncopen("/mesonet/data/iemre/%s_iemre_%s.nc" % (year, table))
    ncvars = OrderedDict()
    for vname in nc.variables.keys():
        if vname in ['lat', 'lon', 'time', 'hasdata']:
            continue
        ncvars[vname] = nc.variables[vname]

    multi = 24 if table == 'daily' else 1
    for tstep in tqdm(nc.variables['time'][:]):
        date = datetime.datetime(year, 1, 1) + datetime.timedelta(
            hours=int(tstep) * multi)
        if table == 'hourly' and date.month != month:
            continue
        grids = {}
        for vname in ncvars:
            grids[vname] = ncvars[vname][tstep].flatten()
        df = pd.DataFrame(grids)
        df['gid'] = list(range(
            len(nc.dimensions['lat']) * len(nc.dimensions['lon'])))
        df['valid'] = date.strftime(
            "%Y-%m-%d %H:%M+00" if table == 'hourly' else '%Y-%m-%d')
        sio = StringIO()
        df.to_csv(sio, sep='\t', header=False, index=False, na_rep='null')
        sio.seek(0)
        cursor = pgconn.cursor()
        cursor.copy_from(sio, dbtable, columns=df.columns, null='null')
        cursor.close()
        pgconn.commit()


if __name__ == '__main__':
    main(sys.argv)
