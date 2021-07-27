"""Need to fix some corrupted n0r NEXRAD color tables!"""
import datetime
import subprocess
import os

import numpy as np
import osgeo.gdal as gdal
from osgeo import gdalconst
from pyiem.util import get_dbconn

PGCONN = get_dbconn("mesosite", user="nobody")
CURSOR = PGCONN.cursor()


def get_colortable(prod):
    """Get the color table for this prod

    Args:
      prod (str): product to get the table for

    Returns:
      colortable

    """
    CURSOR.execute(
        "select r,g,b from iemrasters_lookup l JOIN iemrasters r on "
        "(r.id = l.iemraster_id) WHERE r.name = %s ORDER by l.coloridx ASC",
        ("composite_" + prod,),
    )
    ct = gdal.ColorTable()
    for i, row in enumerate(CURSOR):
        ct.SetColorEntry(i, (row[0], row[1], row[2], 255))
    return ct


n0rct = get_colortable("n0r")


def do(ts):
    """Process!"""
    fn = ts.strftime("n0r_%Y%m%d%H%M.png")
    n0r = gdal.Open(fn)
    n0rd = n0r.ReadAsArray()
    # for i in range(50):
    #    print("%s %s" % (i, np.sum(np.where(n0rd > i, 1, 0))))
    n0rd = np.where(n0rd > 19, 0, n0rd)

    out_driver = gdal.GetDriverByName("gtiff")
    outdataset = out_driver.Create(
        "tmp.tiff",
        n0r.RasterXSize,
        n0r.RasterYSize,
        n0r.RasterCount,
        gdalconst.GDT_Byte,
    )
    # Set output color table to match input
    outdataset.GetRasterBand(1).SetRasterColorTable(n0rct)
    outdataset.GetRasterBand(1).WriteArray(n0rd)
    del outdataset
    subprocess.call(
        "convert -define PNG:preserve-colormap tmp.tiff tmp.png", shell=True
    )

    os.unlink("tmp.tiff")
    subprocess.call(f"mv tmp.png {fn}", shell=True)


def main():
    """Go Main"""
    sts = datetime.datetime(1997, 1, 1, 12, 5)
    ets = datetime.datetime(1997, 1, 1, 12, 45)
    interval = datetime.timedelta(minutes=5)
    now = sts
    while now < ets:
        do(now)
        now += interval


if __name__ == "__main__":
    main()
