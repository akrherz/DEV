"""Convert PRISM to swat files

1981 thru 2017
"""
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

GRIDINFO = namedtuple("GridInfo", ["x0", "y0", "xsz", "ysz", "mask"])
PROJSTR = "+proj=longlat +datum=WGS84 +no_defs"


def get_basedate(ncfile):
    """Compute the dates that we have"""
    nctime = ncfile.variables["time"]
    basets = datetime.datetime.strptime(
        nctime.units, "Days since %Y-%m-%d 00:00:0.0"
    )
    ts = basets + datetime.timedelta(days=float(nctime[0]))
    return datetime.date(ts.year, ts.month, ts.day), len(nctime[:])


def main(argv):
    """Go Main Go"""
    basedir = "/mesonet/data/prism"
    outdir = "swatfiles_prism_arealaverage"
    if os.path.isdir(outdir):
        print("ABORT: as %s exists" % (outdir,))
        return
    os.mkdir(outdir)
    for dirname in ["precipitation", "temperature"]:
        os.mkdir("%s/%s" % (outdir, dirname))
    pgconn = get_dbconn("idep")
    myhucs = [x.strip() for x in open("myhucs.txt")]
    huc8df = gpd.GeoDataFrame.from_postgis(
        """
    SELECT huc_12, ST_Transform(simple_geom, %s) as geo from huc12
    WHERE scenario = 0 and huc_12 in %s ORDER by huc12
    """,
        pgconn,
        params=(PROJSTR, tuple(myhucs)),
        index_col="huc_12",
        geom_col="geo",
    )
    hucs = huc8df.index.values
    assert len(hucs) == len(myhucs)
    years = range(1981, 2021)
    nc = netCDF4.Dataset("%s/%s_daily.nc" % (basedir, years[0]))

    # compute the affine
    ncaffine = Affine(
        nc.variables["lon"][1] - nc.variables["lon"][0],
        0.0,
        nc.variables["lon"][0],
        0.0,
        nc.variables["lat"][0] - nc.variables["lat"][1],
        nc.variables["lat"][-1],
    )
    czs = CachingZonalStats(ncaffine)
    nc.close()

    fps = []
    for year in years:
        nc = netCDF4.Dataset("%s/%s_daily.nc" % (basedir, year))
        basedate, timesz = get_basedate(nc)
        for i in tqdm(range(timesz), desc=str(year)):
            # date = basedate + datetime.timedelta(days=i)

            # keep array logic in top-down order
            tasmax = np.flipud(nc.variables["tmax"][i, :, :])
            tasmin = np.flipud(nc.variables["tmin"][i, :, :])
            pr = np.flipud(nc.variables["ppt"][i, :, :])
            mytasmax = czs.gen_stats(tasmax, huc8df["geo"])
            mytasmin = czs.gen_stats(tasmin, huc8df["geo"])
            mypr = czs.gen_stats(pr, huc8df["geo"])
            for j, huc12 in enumerate(hucs):
                if i == 0 and year == years[0]:
                    fps.append(
                        [
                            open(
                                ("%s/precipitation/P%s.txt") % (outdir, huc12),
                                "w",
                            ),
                            open(
                                ("%s/temperature/T%s.txt") % (outdir, huc12),
                                "w",
                            ),
                        ]
                    )
                    fps[j][0].write("%s\n" % (basedate.strftime("%Y%m%d"),))
                    fps[j][1].write("%s\n" % (basedate.strftime("%Y%m%d"),))

                fps[j][0].write(("%.1f\n") % (mypr[j],))
                fps[j][1].write(("%.2f,%.2f\n") % (mytasmax[j], mytasmin[j]))
        nc.close()
    for fp in fps:
        fp[0].close()
        fp[1].close()


if __name__ == "__main__":
    main(sys.argv)
