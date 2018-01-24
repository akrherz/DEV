"""attempt a NLDN plot of days since"""
from __future__ import print_function
import datetime

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from pyiem.util import get_dbconn
from pyiem import reference
from pyiem.plot import MapPlot

GX = 0.05


def main():
    """Go Main Go"""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()
    sts = datetime.date(2018, 1, 24)
    ets = datetime.date(2017, 8, 1)
    now = sts
    xaxis = np.arange(reference.IA_WEST, reference.IA_EAST, GX)
    yaxis = np.arange(reference.IA_SOUTH, reference.IA_NORTH, GX)
    """
    days = np.ones((len(yaxis), len(xaxis)), 'i') * -1

    count = 0
    while now >= ets:
        cursor.execute(""
        select distinct st_x(geom) as lon, st_y(geom) as lat
        from nldn_all n, states s
        WHERE n.valid >= %s and n.valid < %s
        and s.state_abbr = 'IA' and n.geom && s.the_geom
        "", (now, now + datetime.timedelta(days=1)))
        print("date: %s rows: %s" % (now, cursor.rowcount))
        for row in cursor:
            yidx = int((row[1] - reference.IA_SOUTH) / GX)
            xidx = int((row[0] - reference.IA_WEST) / GX)
            if days[yidx, xidx] < 0:
                days[yidx, xidx] = count
        now -= datetime.timedelta(days=1)
        count += 1

    np.save('days', days)
    """
    days = np.load('days.npy')
    mp = MapPlot()
    ramp = [1, 24, 55, 85, 116, 146, 177]
    mp.pcolormesh(xaxis, yaxis, days, ramp,
                  cmap=plt.get_cmap('afmhot_r'))
    mp.postprocess(filename='test.png')
    mp.close()


if __name__ == '__main__':
    main()
