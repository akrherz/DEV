"""Create simple timeseries files."""
import os

from tqdm import tqdm
import pandas as pd
from pyiem.util import logger
import osgeo.gdal as gdal

LOG = logger()
FMT = "%Y-%m-%d %H:%M"


def main():
    """Go Main Go."""
    jobs = []
    for line in open("QUEUE"):
        lon, lat, fn = line.strip().split()
        y = int(900 - (float(lat) * 10))
        x = int(1800 - (float(lon) * -10))
        jobs.append([x, y, open(fn, "w")])
        jobs[-1][2].write("valid,precip_mm\n")
    dates = pd.date_range(
        "2007/01/01",
        "2021/01/01 07:00",
        freq="1800s",
    )
    progress = tqdm(dates)
    for dt in progress:
        progress.set_description(dt.strftime("%Y%m%d%H%M"))
        fn = dt.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/" "GIS/imerg/p30m_%Y%m%d%H%M.png"
        )
        if not os.path.isfile(fn):
            for j in jobs:
                j[2].write("%s,%.2f\n" % (dt.strftime(FMT), 0))
        else:
            data = gdal.Open(fn).ReadAsArray()
            for j in jobs:
                imgval = data[j[1], j[0]]
                if imgval < 200:
                    precip = imgval * 0.25
                else:
                    precip = 50.0 + (imgval - 200)
                j[2].write("%s,%.2f\n" % (dt.strftime(FMT), precip))

    for j in jobs:
        j[2].close()


if __name__ == "__main__":
    main()
