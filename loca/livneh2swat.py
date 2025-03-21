"""Dump livneh (LOCA baseline) to SWAT

1989 thru 2010
"""

import datetime
import os
from collections import namedtuple

import geopandas as gpd
import numpy as np
from affine import Affine
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import get_dbconn, ncopen
from tqdm import tqdm

GRIDINFO = namedtuple("GridInfo", ["x0", "y0", "xsz", "ysz", "mask"])
PROJSTR = "+proj=longlat +datum=WGS84 +no_defs"


def get_basedate(ncfile):
    """Compute the dates that we have"""
    nctime = ncfile.variables["time"]
    basets = datetime.datetime.strptime(
        nctime.units, "days since %Y-%m-%d 00:00:00"
    )
    ts = basets + datetime.timedelta(days=float(nctime[0]))
    return datetime.date(ts.year, ts.month, ts.day), len(nctime[:])


def main():
    """Go Main Go"""
    basedir = "/mnt/nrel/akrherz/livneh"
    outdir = "swatfiles_livneh"
    if os.path.isdir(outdir):
        print("ABORT: as %s exists" % (outdir,))
        return
    os.mkdir(outdir)
    for dirname in ["precipitation", "temperature"]:
        os.mkdir("%s/%s" % (outdir, dirname))
    pgconn = get_dbconn("idep")
    huc12df = gpd.GeoDataFrame.from_postgis(
        """
    SELECT huc12, ST_Transform(simple_geom, %s) as geo from wbd_huc12
    WHERE swat_use ORDER by huc12
    """,
        pgconn,
        params=(PROJSTR,),
        index_col="huc12",
        geom_col="geo",
    )
    hucs = huc12df.index.values
    years = range(1989, 2011)
    nc = ncopen("%s/livneh_NAmerExt_15Oct2014.198109.nc" % (basedir,))

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
            nc = ncopen(
                ("%s/livneh_NAmerExt_15Oct2014.%s%02i.nc")
                % (basedir, year, month)
            )
            basedate, timesz = get_basedate(nc)
            for i in tqdm(range(timesz), desc="%s%02i" % (year, month)):
                tasmax = np.flipud(nc.variables["Tmax"][i, :, :])
                tasmin = np.flipud(nc.variables["Tmin"][i, :, :])
                pr = np.flipud(nc.variables["Prec"][i, :, :])
                mytasmax = czs.gen_stats(tasmax, huc12df["geo"])
                mytasmin = czs.gen_stats(tasmin, huc12df["geo"])
                mypr = czs.gen_stats(pr, huc12df["geo"])
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
                    fps[j][0].write(
                        ("%.1f\n") % (mypr[j] if mypr[j] is not None else 0,)
                    )
                    fps[j][1].write(
                        ("%.2f,%.2f\n") % (mytasmax[j], mytasmin[j])
                    )

    for fp in fps:
        fp[0].close()
        fp[1].close()


if __name__ == "__main__":
    main()
