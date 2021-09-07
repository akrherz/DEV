"""Create simple timeseries files."""
import sys
import os

from tqdm import tqdm
import pandas as pd
from pyiem.util import logger
import osgeo.gdal as gdal

LOG = logger()


def main(argv):
    """Go Main Go."""
    lon = float(argv[1])
    lat = float(argv[2])
    if len(argv) > 3:
        outfn = argv[3]
    else:
        outfn = "imerg_%s_%s.csv" % (lon, lat)
    # Ankeny 41.74373,-93.5909
    y = int(900 - (lat * 10))
    x = int(1800 - (lon * -10))
    LOG.info("Running for lon:%s lat:%s y:%s x:%s", lon, lat, y, x)
    dates = pd.date_range(
        "2007/01/01",
        "2021/01/01 07:00",
        freq="1800s",
    )
    progress = tqdm(dates)
    with open(outfn, "w") as outfp:
        outfp.write("valid,accum_mm\n")
        for dt in progress:
            progress.set_description(dt.strftime("%Y%m%d%H%M"))
            fn = dt.strftime(
                "/mesonet/ARCHIVE/data/%Y/%m/%d/"
                "GIS/imerg/p30m_%Y%m%d%H%M.png"
            )
            if not os.path.isfile(fn):
                precip = 0
            else:
                data = gdal.Open(fn).ReadAsArray()
                imgval = data[y, x]
                if imgval < 200:
                    precip = imgval * 0.25
                else:
                    precip = 50.0 + (imgval - 200)
            outfp.write("%s,%.2f\n" % (dt.strftime("%Y-%m-%d %H:%M"), precip))


if __name__ == "__main__":
    main(sys.argv)
