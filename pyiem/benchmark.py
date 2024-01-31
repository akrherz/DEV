"""Why so slow."""
import time

from pyiem.plot.geoplot import MapPlot
from pyiem.util import logger

LOG = logger()


def myfunc():
    """GO Main Go."""
    mp = MapPlot(sector="conus", title="Four Counties", nocaption=True)
    data = {"IAC001": 10, "AKC013": 20, "HIC001": 30, "PRC001": 40}
    mp.fill_ugcs(data)
    mp.fig.savefig("/tmp/cities.png")
    mp.close()


def main():
    """Profile this."""
    import cProfile
    import pstats

    sts = time.perf_counter()
    with cProfile.Profile() as pr:
        myfunc()
    LOG.info("myfunc took %.4f seconds", time.perf_counter() - sts)

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    # write stats to .prof file for snakeviz to read
    stats.dump_stats("benchmark.prof")


if __name__ == "__main__":
    main()
