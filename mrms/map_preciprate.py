"""Plot MRMS PrecipRate."""

import datetime
import gzip
import os
import tempfile
from zoneinfo import ZoneInfo

import click
import numpy as np
import pygrib
from pyiem import mrms
from pyiem.plot import MapPlot
from pyiem.plot.colormaps import maue
from pyiem.util import logger

LOG = logger()


def workflow(valid, framei):
    """Generate for this timestep!"""
    # minutes = 2 if valid.year > 2011 else 5
    gribfn = mrms.fetch("PrecipRate", valid)
    # http://www.nssl.noaa.gov/projects/mrms/operational/tables.php
    # Says units are mm/hr
    fp = gzip.GzipFile(gribfn, "rb")
    (_, tmpfn) = tempfile.mkstemp()
    with open(tmpfn, "wb") as fh:
        try:
            fh.write(fp.read())
        except EOFError:
            LOG.info("caught EOFError on %s, likely corrupt, deleting", gribfn)
            os.unlink(gribfn)
            return
    grbs = pygrib.open(tmpfn)
    grb = grbs[1]
    lats, lons = grb.latlons()
    grbs.close()
    os.unlink(tmpfn)
    os.unlink(gribfn)

    val = grb["values"]
    # If has a mask, convert those to -3
    if hasattr(val, "mask"):
        val = np.where(val.mask, -3, val)
    val = val

    lts = valid.astimezone(ZoneInfo("America/Chicago"))
    mp = MapPlot(
        logo="dep",
        caption="Daily Erosion Project",
        title="MRMS 2 Minute Precipitation Rate mm/hr",
        subtitle=f"{lts:%d %b %Y %I:%M %p %Z}",
    )
    clevels = np.arange(0, 100.1, 5)
    clevels[0] = 0.01
    yslice = slice(1100, 2000)
    xslice = slice(3000, 4000)
    cmap = maue()
    cmap.set_under("white")
    mp.pcolormesh(
        lons[yslice, xslice],
        lats[yslice, xslice],
        val[yslice, xslice],
        clevels,
        cmap=cmap,
        units="mm/hr",
    )
    mp.drawcounties()
    mp.fig.savefig(f"frames/{framei:05.0f}.png")
    mp.close()


@click.command()
@click.option("--valid", type=click.DateTime(), help="UTC Timestamp")
@click.option("--frames", type=int, default=0, help="Frames")
def main(valid, frames):
    """Go Main Go"""
    valid = valid.replace(tzinfo=datetime.timezone.utc)
    for i in range(0, frames + 1):
        workflow(valid + datetime.timedelta(minutes=i * 2), i)


if __name__ == "__main__":
    main()
