# Compute mean depatures at or around a holiday

import matplotlib.pyplot as plt
import mx.DateTime
import numpy
from pyiem.util import get_dbconn

COOP = get_dbconn("coop")
ccursor = COOP.cursor()

highs = []
lows = []
for yr in range(1978, 2010):
    nov1 = mx.DateTime.DateTime(yr, 11, 1)
    turkey = nov1 + mx.DateTime.RelativeDateTime(
        weekday=(mx.DateTime.Thursday, 4)
    )
    sql = (
        "SELECT day, high, low, "
        "case when precip > 0.005 THEN 1 else 0 end as precip, "
        "case when snow > 0.005 then 1 else 0 end as snow from alldata "
        "WHERE stationid = '%s' and day = '%s'"
    ) % ("ia2203", turkey)
    ccursor.execute(sql)
    row = ccursor.fetchone()
    highs.append(row[1])
    lows.append(row[2])

highs.append(25)
lows.append(18)


h = numpy.array(highs)
ll = numpy.array(lows)

fig = plt.figure(1, figsize=(8, 8))
ax = fig.add_subplot(111)


def mod_rects(rects):
    for rect in rects:
        if (rect.get_y() + rect.get_height()) < 32:
            rect.set_facecolor("b")


rects = ax.bar(
    numpy.arange(1978, 2011) - 0.4, h - ll, bottom=ll, facecolor="r"
)
mod_rects(rects)
ax.set_xlim(1977.5, 2010.5)
ax.set_xlabel("Year, * 2010 Data Forecasted")
ax.set_title("Des Moines Thanksgiving High & Low Temperature")
ax.set_ylabel(r"Temperature $^{\circ}\mathrm{F}$")
# ax.set_xticks( numpy.arange(1895,2015,5) )
ax.grid(True)

fig.savefig("test.png")
