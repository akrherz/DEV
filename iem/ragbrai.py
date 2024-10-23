"""Useful."""

import math
from datetime import datetime

import matplotlib.pyplot as plt
import numpy
from pyiem.util import get_dbconn

ASOS = get_dbconn("asos")
acursor = ASOS.cursor()


def uv(sped, drct2):
    dirr = drct2 * math.pi / 180.00
    s = math.sin(dirr)
    c = math.cos(dirr)
    u = round(-sped * s, 2)
    v = round(-sped * c, 2)
    return u, v


DATES = [
    [datetime(1973, 8, 26), datetime(1973, 8, 31)],
    [datetime(1974, 8, 4), datetime(1974, 8, 10)],
    [datetime(1975, 8, 3), datetime(1975, 8, 9)],
    [datetime(1976, 8, 1), datetime(1976, 8, 7)],
    [datetime(1977, 7, 31), datetime(1977, 8, 6)],
    [datetime(1978, 7, 30), datetime(1978, 8, 5)],
    [datetime(1979, 7, 29), datetime(1979, 8, 4)],
    [datetime(1980, 7, 27), datetime(1980, 8, 2)],
    [datetime(1981, 7, 26), datetime(1981, 8, 1)],
    [datetime(1982, 7, 25), datetime(1982, 7, 31)],
    [datetime(1983, 7, 24), datetime(1983, 7, 30)],
    [datetime(1984, 7, 22), datetime(1984, 7, 28)],
    [datetime(1985, 7, 21), datetime(1985, 7, 27)],
    [datetime(1986, 7, 20), datetime(1986, 7, 26)],
    [datetime(1987, 7, 19), datetime(1987, 7, 25)],
    [datetime(1988, 7, 24), datetime(1988, 7, 30)],
    [datetime(1989, 7, 22), datetime(1989, 7, 28)],
    [datetime(1990, 7, 22), datetime(1990, 7, 28)],
    [datetime(1991, 7, 21), datetime(1991, 7, 27)],
    [datetime(1992, 7, 19), datetime(1992, 7, 25)],
    [datetime(1993, 7, 25), datetime(1993, 7, 31)],
    [datetime(1994, 7, 24), datetime(1994, 7, 30)],
    [datetime(1995, 7, 23), datetime(1995, 7, 29)],
    [datetime(1996, 7, 21), datetime(1996, 7, 27)],
    [datetime(1997, 7, 20), datetime(1997, 7, 26)],
    [datetime(1998, 7, 19), datetime(1998, 7, 25)],
    [datetime(1999, 7, 25), datetime(1999, 7, 31)],
    [datetime(2000, 7, 23), datetime(2000, 7, 29)],
    [datetime(2001, 7, 22), datetime(2001, 7, 28)],
    [datetime(2002, 7, 21), datetime(2002, 7, 27)],
    [datetime(2003, 7, 20), datetime(2003, 7, 26)],
    [datetime(2004, 7, 25), datetime(2004, 7, 31)],
    [datetime(2005, 7, 24), datetime(2005, 7, 30)],
    [datetime(2006, 7, 23), datetime(2006, 7, 29)],
    [datetime(2007, 7, 22), datetime(2007, 7, 28)],
    [datetime(2008, 7, 20), datetime(2008, 7, 26)],
    [datetime(2009, 7, 19), datetime(2009, 7, 25)],
    [datetime(2010, 7, 25), datetime(2010, 7, 31)],
    [datetime(2011, 7, 24), datetime(2011, 7, 30)],
    [datetime(2012, 7, 22), datetime(2012, 7, 28)],
    [datetime(2013, 7, 21), datetime(2013, 7, 27)],
    [datetime(2014, 7, 20), datetime(2014, 7, 26)],
]

hindex = numpy.zeros((2015 - 1973))
uwnd = numpy.zeros((2015 - 1973))

# output = open('ragbrai.dat', 'w')
for sdate, edate in DATES:
    acursor.execute(
        """
    SELECT tmpf, dwpf, sknt, drct, valid, feel from t%s WHERE station = 'DSM'
    and valid BETWEEN '%s 00:00' and '%s 23:59' and tmpf > 0
    and dwpf > 0 and sknt >= 0 and drct >= 0 ORDER by valid ASC
    """
        % (sdate.year, sdate.strftime("%Y-%m-%d"), edate.strftime("%Y-%m-%d"))
    )
    cnt = 0
    tot = 0
    ttot = 0
    utot = 0
    ucnt = 0
    vtot = 0
    for row in acursor:
        ttot += row[0]
        h = row[5]
        if row[4].hour > 5 and row[4].hour < 22:
            u, v = uv(row[2], row[3])
            # output.write("%s,%s,%s,%.1f,%.2f,%.2f\n" % (
            # row[4].strftime("%Y,%m,%d,%H,%M"), row[0], row[1], h, u, v))
            utot += u
            vtot += v
            ucnt += 1
        tot += h
        cnt += 1
    print(
        "%s %3s %4.1f %4.1f %4.1f %4.1f"
        % (
            sdate.year,
            cnt,
            ttot / float(cnt),
            tot / float(cnt),
            utot / float(ucnt),
            vtot / float(ucnt),
        )
    )
    uwnd[sdate.year - 1973] = utot / float(ucnt) * 1.15
    hindex[sdate.year - 1973] = tot / float(cnt)
# output.close()


fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_xlim(1972.5, 2014.5)
ax.set_title("1973-2014 RAGBRAI Weather (Des Moines Airport Data)")
ax.bar(numpy.arange(1973, 2015) - 0.4, hindex, color="r")
ax.set_ylim(60, 100)
ax.set_ylabel("Average Heat Index $^{\circ}\mathrm{F}$")
ax.grid(True)

ax2 = fig.add_subplot(212)
ax2.set_xlim(1972.5, 2014.5)
bars = ax2.bar(numpy.arange(1973, 2015) - 0.4, uwnd, fc="r")
for bar in bars:
    if bar.get_xy()[1] == 0:
        bar.set_facecolor("g")
ax2.set_ylabel("East/West Daytime\n Average Wind Speed [mph]")
ax2.text(1990, 5, "Tail-winds")
ax2.text(1990, -5, "Head-winds")

ax2.grid(True)

fig.savefig("test.png")
