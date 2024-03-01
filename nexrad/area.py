"""Old Plot."""

import datetime

import numpy as np
import osgeo.gdal as gdal

from pyiem import reference


def lalo2pt(lon, lat):
    """Simple."""
    x = int((-126.0 - lon) / -0.01)
    y = int((50.0 - lat) / 0.01)
    return x, y


def main():
    """Go Main Go."""
    sts = datetime.datetime(2014, 4, 7, 11, 0)
    ets = datetime.datetime(2014, 4, 8, 2, 5)
    interval = datetime.timedelta(minutes=5)

    x1, y1 = lalo2pt(reference.IA_WEST, reference.IA_SOUTH)
    x2, y2 = lalo2pt(reference.IA_EAST, reference.IA_NORTH)

    sz = (y1 - y2) * (x2 - x1)

    now = sts
    while now < ets:
        fp = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png"
        )
        n0r = gdal.Open(fp, 0)
        n0rd = n0r.ReadAsArray()
        data = n0rd[y2:y1, x1:x2]
        dbz = (data - 7.0) * 5.0
        print(
            "%s,%.2f"
            % (
                now.strftime("%Y%m%d%H%M"),
                np.sum(np.where(dbz >= 10, 1, 0)) / float(sz) * 100.0,
            )
        )
        now += interval


if __name__ == "__main__":
    main()
