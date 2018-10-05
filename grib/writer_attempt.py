"""see if we can properly write a grib file."""
import datetime

import eccodes
import ncepgrib2
import pygrib
from pyiem.util import utc


def attempt3():
    """See what eccodes does."""
    grbs = eccodes.GribFile('p06m_2018100500f006.grb')
    for grb in grbs:
        print(grb)


def attempt2():
    """See what ncepgrib2 does."""
    grbs = ncepgrib2.Grib2Decode('p06m_2018100500f006.grb')
    print(dir(grbs))


def main():
    """Go Main Go."""
    f0 = utc(2018, 10, 5, 0)
    fx = f0 + datetime.timedelta(hours=168)
    grbs = pygrib.open('p06m_2018100500f006.grb')
    grb = grbs[1]
    """
    keys = list(grb.keys())
    keys.sort()
    for key in keys:
        try:
            print("%s %s" % (key, getattr(grb, key, None)))
        except RuntimeError as exp:
            print("%s None" % (key, ))
    """
    grb['dayOfEndOfOverallTimeInterval'] = fx.day
    grb['endStep'] = 168
    grb['hourOfEndOfOverallTimeInterval'] = fx.hour
    grb['lengthOfTimeRange'] = 168
    grb['stepRange'] = "0-168"
    grb = pygrib.reload(grb)
    # grb['validityDate'] = int(fx.strftime("%Y%m%d"))
    # grb['validityTime'] = int(fx.strftime("%H%M"))
    fp = open('test.grb', 'wb')
    fp.write(grb.tostring())
    fp.close()


if __name__ == '__main__':
    # attempt2()
    attempt3()
    # main()
