"""Merge the 0.01x0.01 Q3 24 hour precip data estimates"""
import datetime
import gzip
import os
import sys
import tempfile

import numpy as np
import pygrib

from pyiem import iemre
from pyiem.mrms import WEST, fetch
from pyiem.util import logger, ncopen, utc

LOG = logger()
TMP = "/mesonet/tmp"


def run(date):
    """Run 6z to 6z."""
    # Data is in the rears
    now = utc(date.year, date.month, date.day, 6)
    ets = now + datetime.timedelta(hours=24)
    lats = None
    total = None
    while now < ets:
        now += datetime.timedelta(minutes=5)
        fn = fetch("PrecipRate", now)
        if fn is None:
            LOG.info("No data for %s", now)
            continue
        with gzip.GzipFile(fn, "rb") as fp:
            (_, gribfn) = tempfile.mkstemp()
            with open(gribfn, "wb") as fh:
                fh.write(fp.read())
        os.unlink(fn)
        grbs = pygrib.open(gribfn)
        grb = grbs[1]
        if lats is None:
            lats, _ = grb.latlons()
        # mm / hr over 5 minutes to accum
        val = grb.values
        grbs.close()
        os.unlink(gribfn)
        if hasattr(val, "mask"):
            val = np.where(val.mask, -3, val)

        val = val / 60.0 * 5.0

        # Anything less than zero, we set to zero
        val = np.where(val < 0, 0, val)
        if total is None:
            total = val
        else:
            total += val

    offset = iemre.daily_offset(date)
    if lats is None:
        LOG.warning("No data found for %s, using zeros", date)
        with ncopen(iemre.get_daily_mrms_ncname(date.year), "a") as nc:
            ncprecip = nc.variables["p01d"]
            ncprecip[offset, :, :] = 0
        return

    # CAREFUL HERE!  The MRMS grid is North to South
    # set top (smallest y)
    y0 = int((lats[0, 0] - iemre.NORTH) * 100.0)
    y1 = int((lats[0, 0] - iemre.SOUTH) * 100.0)
    x0 = int((iemre.WEST - WEST) * 100.0)
    x1 = int((iemre.EAST - WEST) * 100.0)
    with ncopen(iemre.get_daily_mrms_ncname(date.year), "a") as nc:
        ncprecip = nc.variables["p01d"]
        ncprecip[offset, :, :] = np.flipud(total[y0:y1, x0:x1])


def main(argv):
    """go main go"""
    date = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    run(date)


if __name__ == "__main__":
    main(sys.argv)
