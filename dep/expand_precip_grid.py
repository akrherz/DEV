"""A one-off expansion of the precip grid files."""
import os
import gzip

import numpy as np
import pandas as pd
from pyiem.dep import SOUTH, NORTH, EAST, WEST


def main():
    """Go."""
    shp = (int((NORTH - SOUTH) * 100), int((EAST - WEST) * 100))

    for dt in pd.date_range("2007/01/01", "2022/06/24"):
        fn = dt.strftime("/mnt/idep2/data/dailyprecip/%Y/%Y%m%d.npy")
        if not os.path.isfile(fn):
            continue
        newp = np.zeros(shp)
        oldp = np.load(fn)
        # grid inserted at 35N, 104W
        newp[1200:2600, 2200:5200] = oldp
        with gzip.GzipFile(f"{fn}.gz", "w") as fh:
            np.save(fh, newp)


if __name__ == "__main__":
    main()
