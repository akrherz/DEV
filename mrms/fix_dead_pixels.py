"""We found some near zero pixels in the 2015 file."""

import numpy as np
from pyiem.grid.nav import MRMS_IEMRE
from pyiem.util import ncopen
from tqdm import tqdm


def main():
    """Go Main Go."""
    queue = []
    with ncopen("/mesonet/data/mrms/2015_mrms_daily.nc") as nc:
        for lon in tqdm(np.arange(-99.0, -96, 0.01)):
            for lat in np.arange(38, 42, 0.01):
                i, j = MRMS_IEMRE.find_ij(lon, lat)
                val = np.sum(nc.variables["p01d"][:, j, i])
                if val < 100:
                    print("%s %s %s" % (lon, lat, val))
                    queue.append((j, i))

    with ncopen("/mesonet/data/mrms/2015_mrms_daily.nc", "a") as nc:
        p01d = nc.variables["p01d"]
        for j, i in queue:
            oldsum = np.sum(p01d[:, j, i])
            newsum = np.sum(p01d[:, j + 10, i + 10])
            p01d[:, j, i] = p01d[:, j + 10, i + 10]
            print(j, i, oldsum, newsum)


if __name__ == "__main__":
    main()
