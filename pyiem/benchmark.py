"""Why so slow."""

from pyiem.plot.geoplot import MapPlot
from pyiem.util import logger

LOG = logger()


def main():
    """GO Main Go."""
    LOG.info("Construct")
    mp = MapPlot(sector="nws", title="Four Counties", nocaption=True)
    data = {"IAC001": 10, "AKC013": 20, "HIC001": 30, "PRC001": 40}
    LOG.info("fill_ugcs")
    mp.fill_ugcs(data)
    LOG.info("savefig")
    mp.fig.savefig("/tmp/cities.png")
    LOG.info("close")
    mp.close()


if __name__ == "__main__":
    main()
