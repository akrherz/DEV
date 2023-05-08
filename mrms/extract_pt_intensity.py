"""Extract out a point time-series."""
import datetime
import gzip
import os
import sys
import tempfile

import pygrib

from pyiem.mrms import NORTH, WEST, fetch
from pyiem.util import utc

FN = sys.argv[1]
LAT = float(sys.argv[3])
LON = float(sys.argv[2])
IDXY = int((NORTH - LAT) * 100.0)
IDXX = int((LON - WEST) * 100.0)


def work(gzipfn):
    """Go."""
    fp = gzip.GzipFile(gzipfn, "rb")
    (_, tmpfn) = tempfile.mkstemp()
    with open(tmpfn, "wb") as fh:
        fh.write(fp.read())
    grbs = pygrib.open(tmpfn)
    grb = grbs[1]
    val = grb["values"] / 25.4  # mm/hr to in/hr
    os.unlink(tmpfn)
    return val[IDXY, IDXX]


def main():
    """Go Main Go."""
    now = utc(2020, 7, 15, 0, 30)
    ets = utc(2020, 7, 15, 1, 45)
    interval = datetime.timedelta(minutes=2)
    with open(f"{FN}_{(0 - LON):.2f}W_{LAT:.2f}N.csv", "w") as fh:
        fh.write("VALID_UTC,RAINRATE_IN_HR\n")
        while now < ets:
            gzipfn = fetch("PrecipRate", now)
            val = work(gzipfn)
            fh.write("%s,%.2f\n" % (now.strftime("%Y-%m-%dT%H:%MZ"), val))
            now += interval


if __name__ == "__main__":
    main()
