"""For some years, we only have our IEM n1p RASTERs."""

from datetime import date, datetime, timedelta

import click
import numpy as np
from osgeo import gdal

from pyiem import iemre
from pyiem.util import archive_fetch, logger, ncopen, utc

LOG = logger()
TMP = "/mesonet/tmp"
gdal.UseExceptions()


def run(dt: date, fordep: bool):
    """Run 6z to 6z."""
    # Data is in the rears
    now = utc(dt.year, dt.month, dt.day, 6)
    ets = now + timedelta(hours=18 if fordep else 24)
    total = None
    ncfn = iemre.get_daily_mrms_ncname(dt.year)
    offset = iemre.daily_offset(dt)
    if fordep:
        ncfn = ncfn.replace("daily", "dep")
        offset = offset - iemre.daily_offset(date(dt.year, 4, 11))
    while now < ets:
        now += timedelta(minutes=60)
        ppath = f"{now:%Y/%m/%d}/GIS/mrms/n1p_{now:%Y%m%d%H%M}.png"
        with archive_fetch(ppath) as fn:
            if fn is None:
                LOG.info("No data for %s", ppath)
                continue
            with gdal.Open(fn) as ds:
                data = ds.ReadAsArray()
                if total is None:
                    total = np.zeros(data.shape, np.float32)
                # Convert the color index value to mm
                # Anything over 254 is bad
                res = np.where(data > 254, 0, data)
                res = np.where(
                    np.logical_and(data >= 0, data < 180), data * 0.25, res
                )
                res = np.where(
                    np.logical_and(data >= 180, data < 255),
                    125.0 + ((data - 180) * 5.0),
                    res,
                )
                total += res

    if total is None:
        LOG.warning("No data found for %s, using zeros", dt)
        with ncopen(ncfn, "a") as nc:
            nc.variables["p01d"][offset] = 0
        return

    # CAREFUL HERE!  The MRMS grid is North to South
    # set top (smallest y)
    y0 = int((55.0 - iemre.NORTH) * 100.0)
    y1 = int((55.0 - iemre.SOUTH) * 100.0)
    x0 = int((iemre.WEST + 130) * 100.0)
    x1 = int((iemre.EAST + 130) * 100.0)
    with ncopen(ncfn, "a") as nc:
        ncprecip = nc.variables["p01d"]
        LOG.info(
            "Writing @%s[%s:%s, %s:%s] mean: %.1f max: %.1f",
            offset,
            y0,
            y1,
            x0,
            x1,
            np.mean(total),
            np.max(total),
        )
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
