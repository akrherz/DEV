"""See email from Dr Arritt on 20 Mar 2018 for more detailed info

1979 thru 2000
2039 thur 2060

Updated to now: 1989 thru 2010
"""
from __future__ import print_function
import sys
import os
import datetime
from collections import namedtuple

from tqdm import tqdm
import netCDF4
import numpy as np
from affine import Affine
import geopandas as gpd
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import get_dbconn
from pyiem.datatypes import temperature

GRIDINFO = namedtuple("GridInfo", ['x0', 'y0', 'xsz', 'ysz', 'mask'])
PROJSTR = '+proj=longlat +datum=WGS84 +no_defs'


def get_basedate(ncfile):
    """Compute the dates that we have"""
    nctime = ncfile.variables['time']
    basets = datetime.datetime.strptime(nctime.units,
                                        "days since %Y-%m-%d 00:00:00")
    ts = basets + datetime.timedelta(days=float(nctime[0]))
    return datetime.date(ts.year, ts.month, ts.day), len(nctime[:])


def main(argv):
    """Go Main Go"""
    model = argv[1]
    rcp = argv[2]
    basedir = "/mnt/nrel/akrherz/loca/%s/16th/%s/r1i1p1" % (model, rcp)
    outdir = "swatfiles_%s_%s" % (model, rcp)
    if os.path.isdir(outdir):
        print("ABORT: as %s exists" % (outdir, ))
        return
    os.mkdir(outdir)
    for dirname in ['precipitation', 'temperature']:
        os.mkdir("%s/%s" % (outdir, dirname))
    pgconn = get_dbconn('idep')
    huc12df = gpd.GeoDataFrame.from_postgis("""
    SELECT huc12, ST_Transform(simple_geom, %s) as geo from wbd_huc12
    WHERE swat_use ORDER by huc12
    """, pgconn, params=(PROJSTR,), index_col='huc12', geom_col='geo')
    hucs = huc12df.index.values
    years = range(1989, 2011) if rcp == 'historical' else range(2039, 2061)
    nc = netCDF4.Dataset(("%s/pr/pr_day_%s_%s_r1i1p1"
                          "_%.0f0101-%.0f1231.LOCA_2016-04-02.16th.nc"
                          ) % (basedir, model, rcp, years[0], years[0]))

    # compute the affine
    ncaffine = Affine(nc.variables['lon'][1] - nc.variables['lon'][0],
                      0.,
                      nc.variables['lon'][0] - 360.,
                      0.,
                      nc.variables['lat'][0] - nc.variables['lat'][1],
                      nc.variables['lat'][-1])
    czs = CachingZonalStats(ncaffine)
    nc.close()

    fps = []
    for year in years:
        # assume 2006-2010 is closely represented by rcp45
        if year >= 2006 and year < 2011:
            rcp = 'rcp45'
            basedir = "/mnt/nrel/akrherz/loca/%s/16th/%s/r1i1p1" % (model, rcp)
        pr_nc = netCDF4.Dataset(("%s/pr/pr_day_%s_%s_r1i1p1"
                                 "_%.0f0101-%.0f1231.LOCA_2016-04-02.16th.nc"
                                 ) % (basedir, model, rcp, year, year))
        tasmax_nc = netCDF4.Dataset(("%s/tasmax/tasmax_day_%s_%s_r1i1p1"
                                     "_%.0f0101-%.0f1231.LOCA_"
                                     "2016-04-02.16th.nc"
                                     ) % (basedir, model, rcp, year, year))
        tasmin_nc = netCDF4.Dataset(("%s/tasmin/tasmin_day_%s_%s_r1i1p1"
                                     "_%.0f0101-%.0f1231.LOCA_"
                                     "2016-04-02.16th.nc"
                                     ) % (basedir, model, rcp, year, year))
        basedate, timesz = get_basedate(pr_nc)
        for i in tqdm(range(timesz), desc=str(year)):
            # date = basedate + datetime.timedelta(days=i)

            # keep array logic in top-down order
            tasmax = np.flipud(
                temperature(tasmax_nc.variables['tasmax'][i, :, :],
                            'K').value('C'))
            tasmin = np.flipud(
                temperature(tasmin_nc.variables['tasmin'][i, :, :],
                            'K').value('C'))
            pr = np.flipud(pr_nc.variables['pr'][i, :, :])
            mytasmax = czs.gen_stats(tasmax, huc12df['geo'])
            mytasmin = czs.gen_stats(tasmin, huc12df['geo'])
            mypr = czs.gen_stats(pr, huc12df['geo'])
            for j, huc12 in enumerate(hucs):
                if i == 0 and year == years[0]:
                    fps.append([open(('%s/precipitation/P%s.txt'
                                      ) % (outdir, huc12), 'wb'),
                                open(('%s/temperature/T%s.txt'
                                      ) % (outdir, huc12), 'wb')])
                    fps[j][0].write("%s\n" % (basedate.strftime("%Y%m%d"), ))
                    fps[j][1].write("%s\n" % (basedate.strftime("%Y%m%d"), ))

                fps[j][0].write(("%.1f\n"
                                 ) % (mypr[j] * 86400., ))
                fps[j][1].write(("%.2f,%.2f\n"
                                 ) % (mytasmax[j], mytasmin[j]))

    for fp in fps:
        fp[0].close()
        fp[1].close()


if __name__ == '__main__':
    main(sys.argv)
