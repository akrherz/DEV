"""Review how long our segments are."""
import os
import sys
import glob

from pyiem.dep import read_slp
import numpy as np
from tqdm import tqdm
import pandas as pd

MYHUCS = [x.strip() for x in open("myhucs.txt")]


def dump_data():
    """Generate a file."""
    os.chdir("/i/0/slp")
    data = {"huc12": [], "count": [], "flowpaths": []}
    for huc8 in tqdm(glob.glob("*")):
        os.chdir(huc8)
        for huc4 in glob.glob("*"):
            os.chdir(huc4)
            huc12 = huc8 + huc4
            if huc12 in MYHUCS:
                slpfns = glob.glob("*.slp")
                for slpfn in slpfns:
                    res = read_slp(slpfn)
                    for ofe in res:
                        delta = ofe["x"][1:] - ofe["x"][:-1]
                        minval = np.min(delta)
                        if minval < 1:
                            print(slpfn)
                            print(ofe["x"])
                            print(minval)
                            sys.exit()
            os.chdir("..")
        os.chdir("..")
    df = pd.DataFrame(data)
    df.to_csv("/tmp/data.csv", index=False)


def main():
    """Go Main."""
    dump_data()


if __name__ == "__main__":
    main()
