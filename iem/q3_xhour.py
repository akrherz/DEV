"""Create a plot of the X Hour interval precipitation"""
from __future__ import print_function
import os
import sys
import datetime
import gzip
import tempfile

import numpy as np
import pytz
import pygrib
from pyiem.datatypes import distance
import pyiem.mrms as mrms
from pyiem.plot import MapPlot, nwsprecip

TMP = "/mesonet/tmp"
DATES = """2015-06-03
2015-06-07
2015-06-18
2015-07-13
2015-07-18
2015-07-26
2015-07-28
2015-08-03
2015-08-08
2016-06-01
2016-06-04
2016-06-15
2016-07-06
2016-07-11
2016-07-12
2016-07-17
2016-08-04
2016-08-05
2016-08-11
2017-06-04
2017-06-14
2017-06-17
2017-06-28
2017-07-10
2017-07-22
2017-07-27
2017-08-06
2017-08-22
2017-08-26"""


def doit(ts, hours):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # Start at 1 AM
    total = None
    for gmt in [ts + datetime.timedelta(hours=1),
                ts + datetime.timedelta(hours=2),
                ts + datetime.timedelta(hours=3)]:
        gribfn = None
        for prefix in ['GaugeCorr', 'RadarOnly']:
            gribfn = mrms.fetch(prefix+"_QPE_01H", gmt)
            if gribfn is None:
                continue
            break
        if gribfn is None:
            print("q3_xhour.py[%s] MISSING %s" % (hours, gmt))
            continue
        fp = gzip.GzipFile(gribfn, 'rb')
        (tmpfp, tmpfn) = tempfile.mkstemp()
        tmpfp = open(tmpfn, 'wb')
        tmpfp.write(fp.read())
        tmpfp.close()
        grbs = pygrib.open(tmpfn)
        grb = grbs[1]
        os.unlink(tmpfn)
        # careful here, how we deal with the two missing values!
        if total is None:
            total = grb['values']
        else:
            maxgrid = np.maximum(grb['values'], total)
            total = np.where(np.logical_and(grb['values'] >= 0,
                                            total >= 0),
                             grb['values'] + total, maxgrid)
        os.unlink(gribfn)

    if total is None:
        print("q3_xhour.py no data ts: %s hours: %s" % (ts, hours))
        return

    # Scale factor is 10

    lts = (ts + datetime.timedelta(hours=3)).astimezone(
        pytz.timezone("America/Chicago"))
    subtitle = 'Total up to %s' % (lts.strftime("%d %B %Y %I:%M %p %Z"),)
    mp = MapPlot(sector='midwest',
                 title=("NCEP MRMS Q3 (RADAR+GaugeCorr) %s Hour "
                        "Precipitation [inch]") % (hours,),
                 subtitle=subtitle)

    clevs = [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]

    mp.contourf(mrms.XAXIS, mrms.YAXIS,
                distance(np.flipud(total), 'MM').value('IN'), clevs,
                cmap=nwsprecip())
    mp.drawcounties()
    mp.postprocess(filename="q3_3hr_%s.png" % (ts.strftime("%Y%m%d%H"), ))
    mp.close()


def main2():
    """Hack from above"""
    for date in DATES.split("\n"):
        ts = datetime.datetime.strptime(date, '%Y-%m-%d')
        ts = ts.replace(tzinfo=pytz.utc)
        for hr in [0, 3, 6, 9]:
            ts = ts.replace(hour=hr)
            doit(ts, 3)


def main():
    """Go main"""
    if len(sys.argv) == 7:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]),
                               int(sys.argv[4]), int(sys.argv[5]))
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        doit(ts, int(sys.argv[6]))
    else:
        ts = datetime.datetime.utcnow()
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        doit(ts, int(sys.argv[1]))


if __name__ == "__main__":
    main2()
