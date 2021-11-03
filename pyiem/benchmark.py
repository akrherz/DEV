"""Why so slow."""

from pyiem.plot.geoplot import MapPlot
from pyiem.util import logger
from pyiem.reference import LATLON

LOG = logger()


def main():
    """GO Main Go."""
    LOG.debug("Construct")
    mp = MapPlot(sector="nws", title="Four Counties", nocaption=True)
    data = {"IAC001": 10, "AKC013": 20, "HIC001": 30, "PRC001": 40}
    LOG.debug("fill_ugcs")
    mp.fill_ugcs(data)
    LOG.debug("savefig")
    mp.fig.savefig("/tmp/cities.png")
    LOG.debug("close")
    mp.close()


if __name__ == "__main__":
    main()
