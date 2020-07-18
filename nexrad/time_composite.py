"""An old plot."""
import os
import datetime

from pyiem import iemre
import osgeo.gdal as gdal
import numpy
import netCDF4


def lalo2pt(lat, lon):
    """Simple."""
    x = int((-126.0 - lon) / -0.005)
    y = int((50.0 - lat) / 0.005)
    return x, y


def main():
    """Go Main Go."""
    sts = datetime.datetime(2011, 12, 7, 6)
    ets = datetime.datetime(2011, 12, 8, 0)
    interval = datetime.timedelta(minutes=5)

    # iowa
    # lat0 = 40.38
    # lat1 = 43.50
    # lon0 = -96.64
    # lon1 = -90.14
    lat0 = iemre.SOUTH
    lat1 = iemre.NORTH
    lon0 = iemre.WEST
    lon1 = iemre.EAST
    x0, y0 = lalo2pt(lat1, lon0)
    # lr
    x1, y1 = lalo2pt(lat0, lon1)

    nc = netCDF4.Dataset("time.nc", "w")
    nc.createDimension("latitude", y1 - y0)
    nc.createDimension("longitude", x1 - x0)

    cnts = nc.createVariable("cnt", numpy.float, ("latitude", "longitude"))
    lats = nc.createVariable("lats", numpy.float, ("latitude"))
    lons = nc.createVariable("lons", numpy.float, ("longitude"))

    lats[:] = numpy.arange(lat0, lat1, 0.005)
    lons[:] = numpy.arange(lon0, lon1, 0.005)

    data = numpy.zeros((y1 - y0, x1 - x0), numpy.float)

    now = sts
    while now < ets:
        fp = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0q_%Y%m%d%H%M.png"
        )
        if not os.path.isfile(fp):
            now += interval
            continue
        n0r = gdal.Open(fp, 0)
        n0rd = n0r.ReadAsArray()
        data += numpy.where(n0rd[y0:y1, x0:x1] > 6, 1, 0)
        del n0rd
        del n0r
        now += interval

    cnts[:] = data
    nc.close()


if __name__ == "__main__":
    main()
