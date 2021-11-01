"""Why so slow."""

import cartopy.crs as ccrs
from pyiem.plot.geoplot import MapPlot
from pyiem.util import logger
from pyiem.reference import LATLON

LOG = logger()


def main():
    """GO Main Go."""
    proj = ccrs.PlateCarree()
    LOG.debug("Construct")
    mp = MapPlot(
        sector="custom",
        projection=LATLON,
        west=-120,
        east=-100,
        south=30,
        north=45,
    )
    mp.drawcities()
    LOG.debug("savefig")
    mp.fig.savefig("/tmp/cities.png")
    LOG.debug("close")
    mp.close()


if __name__ == "__main__":
    main()
