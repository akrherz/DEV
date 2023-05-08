"""Old extractor."""
import datetime
import os

import numpy
import osgeo.gdal as gdal


def run(x, y):
    """Do work."""
    sts = datetime.datetime(2013, 1, 16, 0)
    ets = datetime.datetime(2013, 1, 17, 10)
    interval = datetime.timedelta(minutes=5)

    now = sts
    while now < ets:
        fp = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png"
        )
        if not os.path.isfile(fp):
            now += interval
            continue
        n0r = gdal.Open(fp, 0)
        n0rd = n0r.ReadAsArray()
        val = numpy.average(n0rd[y - 2 : y + 2, x - 2 : x + 2])
        print(val)
        now += interval


def main():
    """Go Main GO."""
    lat = 41.6596
    lon = -93.522
    x = int((-126.0 - lon) / -0.01)
    y = int((50.0 - lat) / 0.01)

    run(x, y)


if __name__ == "__main__":
    main()
