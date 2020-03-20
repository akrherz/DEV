"""Convert LIVNEH to swat files

1981 thru 2017
"""
from __future__ import print_function
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
        nctime.units, "Days since %Y-%m-%d 00:00:00"
    )
    ts = basets + datetime.timedelta(days=float(nctime[0]))
    return datetime.date(ts.year, ts.month, ts.day), len(nctime[:])


def main():
    """Go Main Go"""
    basedir = "/mnt/nrel/akrherz/livneh"
    outdir = "swatfiles_livneh_arealaverage"
    if os.path.isdir(outdir):
        print("ABORT: as %s exists" % (outdir,))
        return
    os.mkdir(outdir)
    for dirname in ["precipitation", "temperature"]:
        os.mkdir("%s/%s" % (outdir, dirname))
    pgconn = get_dbconn("idep")
    huc8df = gpd.GeoDataFrame.from_postgis(
        """
    SELECT huc8, ST_Transform(simple_geom, %s) as geo from wbd_huc8
    WHERE swat_use ORDER by huc8
    """,
        pgconn,
        params=(PROJSTR,),
        index_col="huc8",
        geom_col="geo",
    )
    hucs = huc8df.index.values
    years = range(1950, 2014)
    nc = netCDF4.Dataset(
        "%s/livneh_NAmerExt_15Oct2014.%s01.nc" % (basedir, years[0])
    )

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
        for month in range(1, 13):
            nc = netCDF4.Dataset(
                "%s/livneh_NAmerExt_15Oct2014.%s%02i.nc"
                % (basedir, year, month)
            )
            basedate, timesz = get_basedate(nc)
            for i in tqdm(range(timesz), desc="%s %s" % (year, month)):
                # date = basedate + datetime.timedelta(days=i)

                # keep array logic in top-down order
                tasmax = np.flipud(nc.variables["Tmax"][i, :, :])
                tasmin = np.flipud(nc.variables["Tmin"][i, :, :])
                pr = np.flipud(nc.variables["Prec"][i, :, :])
                mytasmax = czs.gen_stats(tasmax, huc8df["geo"])
                mytasmin = czs.gen_stats(tasmin, huc8df["geo"])
                mypr = czs.gen_stats(pr, huc8df["geo"])
                for j, huc12 in enumerate(hucs):
                    if i == 0 and year == years[0] and month == 1:
                        fps.append(
                            [
                                open(
                                    ("%s/precipitation/P%s.txt")
                                    % (outdir, huc12),
                                    "w",
                                ),
                                open(
                                    ("%s/temperature/T%s.txt")
                                    % (outdir, huc12),
                                    "w",
                                ),
                            ]
                        )
                        fps[j][0].write(
                            "%s\n" % (basedate.strftime("%Y%m%d"),)
                        )
                        fps[j][1].write(
                            "%s\n" % (basedate.strftime("%Y%m%d"),)
                        )

                    fps[j][0].write(("%.1f\n") % (mypr[j],))
                    fps[j][1].write(
                        ("%.2f,%.2f\n") % (mytasmax[j], mytasmin[j])
                    )

    for fp in fps:
        fp[0].close()
        fp[1].close()


if __name__ == "__main__":
    main()
