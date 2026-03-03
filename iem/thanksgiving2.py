# Compute mean depatures at or around a holiday

from datetime import date, timedelta

import matplotlib.pyplot as plt
import numpy
from pyiem.database import get_dbconn


def mod_rects(rects):
    for rect in rects:
        if (rect.get_y() + rect.get_height()) < 32:
            rect.set_facecolor("b")


def main():

    COOP = get_dbconn("coop")
    ccursor = COOP.cursor()

    highs = []
    lows = []
    for yr in range(1978, 2010):
        nov1 = date(yr, 11, 1)
        turkey = nov1 + timedelta(days=(3 - nov1.weekday() + 21) % 7 + 21)
        sql = (
            "SELECT day, high, low, "
            "case when precip > 0.005 THEN 1 else 0 end as precip, "
            "case when snow > 0.005 then 1 else 0 end as snow from alldata "
            "WHERE stationid = %s and day = %s"
        )
        ccursor.execute(sql, ("ia2203", turkey))
        row = ccursor.fetchone()
        highs.append(row[1])
        lows.append(row[2])

    highs.append(25)
    lows.append(18)

    h = numpy.array(highs)
    ll = numpy.array(lows)

    fig = plt.figure(1, figsize=(8, 8))
    ax = fig.add_subplot(111)

    rects = ax.bar(
        numpy.arange(1978, 2011) - 0.4, h - ll, bottom=ll, facecolor="r"
    )
    mod_rects(rects)
    ax.set_xlim(1977.5, 2010.5)
    ax.set_xlabel("Year, * 2010 Data Forecasted")
    ax.set_title("Des Moines Thanksgiving High & Low Temperature")
    ax.set_ylabel("Temperature °F")
    ax.grid(True)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
