"""Generic plotter"""
from __future__ import print_function
import datetime
from calendar import month_abbr

import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, drct2text

data = """ KWBC   | 1996-10-31 13:52:00-06
 KBOS   | 1996-10-31 14:00:00-06
 KNYC   | 1996-10-31 14:30:00-06
 KPHL   | 1996-10-31 15:30:00-06
 KALB   | 1996-10-31 17:10:00-06
 KOMA   | 1999-01-05 12:37:00-06
 KLKN   | 2003-11-30 16:24:00-06
 KPHI   | 2004-02-29 02:45:00-06
 KHUN   | 2004-06-30 10:00:00-05
 KMKE   | 2004-07-01 04:24:00-05
 KDSM   | 2004-11-04 16:36:00-06
 KRAP   | 2004-11-22 03:50:00-06
 KBRO   | 2005-01-28 20:00:00-06
 KSHV   | 2006-01-31 16:00:00-06
 KRAH   | 2006-07-01 06:09:00-05
 KCAE   | 2007-07-30 03:52:00-05
 KBOI   | 2008-03-26 16:00:00-05
 KLSX   | 2009-05-26 11:28:00-05
 KEWX   | 2009-05-31 15:36:00-05
 KLUB   | 2010-11-30 21:05:00-06
 KCLE   | 2011-06-30 21:17:00-05
 KRIW   | 2011-08-31 17:12:00-05
 KCYS   | 2011-08-31 17:22:00-05
 KEAX   | 2012-03-11 20:47:00-05
 KAPX   | 2012-04-30 18:42:00-05
 KFFC   | 2013-02-15 04:31:00-06
 KRLX   | 2013-05-07 22:59:00-05
 KFWD   | 2014-03-17 05:21:00-05
 KFSD   | 2015-04-02 10:30:00-05
 KSGF   | 2015-04-15 20:46:00-05
 KLOT   | 2015-10-04 16:30:00-05
 KALY   | 2016-01-06 18:49:00-06
 KLMK   | 2016-04-18 17:02:00-05
 KDLH   | 2016-05-11 11:21:00-05
 KPAH   | 2016-05-31 15:10:00-05
 KJKL   | 2016-08-03 15:35:00-05
 KDDC   | 2016-11-15 20:32:00-06
 PAVW   | 2016-11-20 19:00:00-06
 KOUN   | 2017-10-31 09:16:00-05
 KABQ   | 2018-01-11 20:15:00-06
 KTSA   | 2018-06-26 20:10:00-05
 KOAX   | 2018-07-27 22:29:00-05
 KMPX   | 2018-08-27 04:30:00-05
 KBYZ   | 2018-08-27 06:25:00-05
 KMKX   | 2018-08-27 09:40:00-05
 KLZK   | 2018-08-27 10:52:00-05
 KOKX   | 2018-08-27 14:34:00-05
 KRNK   | 2018-08-27 14:59:00-05
 KGGW   | 2018-08-27 15:35:00-05
 KBOX   | 2018-08-27 15:39:00-05
 KGLD   | 2018-08-27 15:55:00-05
 KSJT   | 2018-08-27 15:58:00-05
 KGRB   | 2018-08-27 16:09:00-05
 TJSJ   | 2018-08-27 16:44:00-05
 KTOP   | 2018-08-27 17:00:00-05
 KICT   | 2018-08-27 17:05:00-05
 KFGF   | 2018-08-27 17:11:00-05
 KDMX   | 2018-08-27 17:28:00-05
 KCTP   | 2018-08-27 17:31:00-05
 KTFX   | 2018-08-27 17:45:00-05
 KBUF   | 2018-08-27 18:16:00-05
 KGID   | 2018-08-27 18:33:00-05
 KMEG   | 2018-08-27 18:35:00-05
 KLWX   | 2018-08-27 18:40:00-05
 KGYX   | 2018-08-27 19:17:00-05
 KBIS   | 2018-08-27 19:58:00-05
 KUNR   | 2018-08-27 20:20:00-05
 KDVN   | 2018-08-27 20:24:00-05
 KLBF   | 2018-08-27 20:28:00-05
 KARX   | 2018-08-27 20:38:00-05
 KILX   | 2018-08-27 20:54:00-05"""



def main():
    """Go Main"""
    vals = {}
    for line in data.split("\n"):
        wfo, valid = line.strip().split("|")
        wfo = wfo.strip()
        year = valid.strip()[:4]
        wfo = wfo[1:]
        if wfo == 'JSJ':
            wfo = 'SJU'
        vals[wfo] = int(year)
    print(vals)
    #bins = [1, 25, 50, 75, 100, 125, 150, 200, 300]
    bins = np.arange(2002, 2019, 2)
    cmap = plt.get_cmap('PuOr')
    mp = MapPlot(sector='nws', continentalcolor='white', figsize=(12., 9.),
                 title=("Year of Last RWS Text Product Issuance"),
                 subtitle=('based on IEM archives'))
    mp.fill_cwas(vals, bins=bins, lblformat='%s',  # , labels=labels,
                 cmap=cmap, ilabel=True,  # clevlabels=clevlabels,
                 units='Year')
    
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
