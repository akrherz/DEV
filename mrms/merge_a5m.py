"""Merge the 0.01x0.01 Q3 24 hour precip data estimates"""

import gzip
import os
import tempfile
from datetime import date, datetime, timedelta

import click
import numpy as np
import pygrib

from pyiem import iemre
from pyiem.mrms import fetch
from pyiem.util import logger, ncopen, utc

LOG = logger()
TMP = "/mesonet/tmp"


def run(dt: date, fordep: bool):
    """Run 6z to 6z."""
    # Data is in the rears
    now = utc(dt.year, dt.month, dt.day, 6)
    ets = now + timedelta(hours=18 if fordep else 24)
    ullat = None
    ullon = None
    total = None
    ncfn = iemre.get_daily_mrms_ncname(dt.year)
    offset = iemre.daily_offset(dt)
    if fordep:
        ncfn = ncfn.replace("daily", "dep")
        offset = offset - iemre.daily_offset(date(dt.year, 4, 11))
    while now < ets:
        now += timedelta(minutes=5)
        fn = fetch("PrecipRate", now)
        if fn is None:
            LOG.info("No data for %s", now)
            continue
        with gzip.GzipFile(fn, "rb") as fp:
            (_, gribfn) = tempfile.mkstemp()
            with open(gribfn, "wb") as fh:
                fh.write(fp.read())
        os.unlink(fn)
        with pygrib.open(gribfn) as grbs:
            grb = grbs[1]
            if ullat is None:
                ullat = grb["latitudeOfFirstGridPointInDegrees"]
                ullon = grb["longitudeOfFirstGridPointInDegrees"]
                if ullon > 0:
                    ullon -= 360
            # mm / hr over 5 minutes to accum
            val = grb.values
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

    if ullon is None:
        LOG.warning("No data found for %s, using zeros", dt)
        with ncopen(ncfn, "a") as nc:
            nc.variables["p01d"][offset] = 0
        return

    # CAREFUL HERE!  The MRMS grid is North to South
    # set top (smallest y)
    y0 = int((ullat - iemre.NORTH) * 100.0)
    y1 = int((ullat - iemre.SOUTH) * 100.0)
    x0 = int((iemre.WEST - ullon) * 100.0)
    x1 = int((iemre.EAST - ullon) * 100.0)
    with ncopen(ncfn, "a") as nc:
        ncprecip = nc.variables["p01d"]
        LOG.info("Writing @%s[%s:%s, %s:%s]", offset, y0, y1, x0, x1)
        ncprecip[offset, :, :] = np.flipud(total[y0:y1, x0:x1])


@click.command()
@click.option(
    "--date", "dt", type=click.DateTime(), help="Date", required=True
)
@click.option("--fordep", is_flag=True, help="For dep")
def main(dt: datetime, fordep: bool):
    """go main go"""
    if fordep and (f"{dt:%m%d}" < "0411" or f"{dt:%m%d}" > "0615"):
        LOG.info("DEP not needed for %s", dt)
        return
    run(dt.date(), fordep)


if __name__ == "__main__":
    main()
