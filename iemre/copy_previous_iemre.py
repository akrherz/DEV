"""Copy the data from the previous IEMRE into our new grid"""
import glob
import os

import netCDF4
import numpy as np
from tqdm import tqdm

from pyiem import iemre


def workflow(fn):
    """Do the copy work"""
    oldnc = netCDF4.Dataset(fn)
    newnc = netCDF4.Dataset(iemre.get_daily_ncname(fn[:4]), "a")
    newnc.set_auto_scale(True)
    i, j = iemre.find_ij(oldnc.variables["lon"][0], oldnc.variables["lat"][0])
    jslice = slice(j, j + oldnc.dimensions["lat"].size * 2)
    islice = slice(i, i + oldnc.dimensions["lon"].size * 2)
    # print("i:%s j:%s %s %s" % (i, j, islice, jslice))
    for vname in tqdm(oldnc.variables):
        if vname in ["time", "lat", "lon"]:
            continue
        for tstep in oldnc.variables["time"][:]:
            oldgrid = np.repeat(
                oldnc.variables[vname][tstep, :, :], 2, 0
            ).repeat(2, 1)
            newnc.variables[vname][tstep, jslice, islice] = oldgrid
    newnc.close()


def main():
    """Do Great Things"""
    os.chdir("/mesonet/data/iemre")
    for fn in glob.glob("????_mw_daily.nc"):
        workflow(fn)


if __name__ == "__main__":
    main()
