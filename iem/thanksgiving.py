"""Compute mean depatures at or around a holiday."""
import sys

import mx.DateTime
import numpy

import matplotlib.pyplot as plt
from pyiem.util import get_dbconn

COOP = get_dbconn("coop")
ccursor = COOP.cursor()


days = []
for yr in range(1880, 2013):
    nov1 = mx.DateTime.DateTime(yr, 11, 1)
    turkey = nov1 + mx.DateTime.RelativeDateTime(
        weekday=(mx.DateTime.Thursday, 4)
    )
    sql = """
        SELECT avg((high+low)/2.0), avg(high) from alldata_ia
        WHERE station = '%s' and day <= '%s' and
        day >= '%s'::date - '%s days'::interval
        and year = %s """ % (
        "IA2203",
        turkey,
        turkey,
        sys.argv[1],
        yr,
    )
    ccursor.execute(sql)
    row = ccursor.fetchone()
    days.append(row[1])

days = numpy.array(days)

fig = plt.figure()
ax = fig.add_subplot(111)

rects = ax.bar(
    numpy.arange(1880, 2013) - 0.4, days, facecolor="b", edgecolor="b"
)
for rect in rects:
    if rect.get_height() >= days[-1]:
        rect.set_edgecolor("r")
        rect.set_facecolor("r")
ax.set_xlim(1879.5, 2012.5)
ax.set_ylim(20, 70)
ax.set_ylabel(r"Average High Temperature $^{\circ}\mathrm{F}$")
ax.set_title(
    "Des Moines [1880-2012] Average High Temperature \n"
    "for week before Thanksgiving (inclusive)"
)
ax.set_xlabel("* 2012 Warmest")
# ax.set_xticks( numpy.arange(1895,2015,5) )
ax.grid(True)

fig.savefig("test.png")
