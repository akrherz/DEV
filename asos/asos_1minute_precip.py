"""One minute precip plot"""
import datetime

import numpy as np
import pytz
import matplotlib.pyplot as plt
import matplotlib.font_manager
from pyiem.util import utc, get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn('asos')
    acursor = pgconn.cursor()

    sts = utc(2018, 7, 17, 18, 0)
    ets = utc(2018, 7, 17, 20, 1)
    tzname = 'America/New_York'
    station = 'DCA'

    sz = int((ets - sts).days * 1440 + (ets - sts).seconds / 60.) + 1

    prec = np.ones((sz,), 'f') * -1

    acursor.execute("""
        SELECT valid, tmpf, dwpf, drct,
        sknt, pres1, gust_sknt, precip from alldata_1minute WHERE station = %s
        and valid >= %s and valid < %s and precip < 1
        ORDER by valid ASC
    """, (station, sts, ets))
    tot = 0
    print("Found %s rows for station" % (acursor.rowcount,))
    for row in acursor:
        offset = int((row[0] - sts).days * 1440 + (row[0] - sts).seconds / 60)
        tot += (row[7] or 0)
        prec[offset] = tot


    # Now we need to fill in the holes
    lastval = 0
    for i in range(sz):
        if prec[i] > -1:
            lastval = prec[i]
        if prec[i] < 0:
            ts = sts + datetime.timedelta(minutes=i)
            print("Missing %s, assigning %s" % (ts, lastval))
            prec[i] = lastval

    rate1 = np.zeros((sz,), 'f')
    rate15 = np.zeros((sz,), 'f')
    rate60 = np.zeros((sz,), 'f')
    for i in range(1, sz):
        rate1[i] = (prec[i] - prec[i-1])*60.
    for i in range(15, sz):
        rate15[i] = (prec[i] - prec[i-15])*4.
    for i in range(60, sz):
        rate60[i] = (prec[i] - prec[i-60])

    xticks = []
    xlabels = []
    lsts = sts.astimezone(pytz.timezone(tzname))
    lets = ets.astimezone(pytz.timezone(tzname))
    interval = datetime.timedelta(minutes=1)
    now = lsts
    i = 0
    while now < lets:
        if now.minute % 5 == 0:
            xticks.append(i)
            fmt = "%-I:%M" if now.minute != 0 else '%-I:%M\n%p'
            xlabels.append(now.strftime(fmt))

        i += 1
        now += interval

    prop = matplotlib.font_manager.FontProperties(size=12)

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    ax.bar(np.arange(sz), rate1, color='b', label="Hourly Rate over 1min",
           zorder=1)
    """
    ax2 = ax.twinx()
    ax2.set_ylabel("Precipitation Accumulation [inch]")
    ax2.plot(np.arange(sz), prec, color='k', label="Accumulation", lw=2,
             zorder=2)
    ax2.set_ylim(0, 16)
    ax2.set_yticks(range(0, 17, 2))
    """
    ax.plot(np.arange(sz), rate15, color='tan', label="Hourly Rate over 15min",
            linewidth=3.5, zorder=3)
    ax.plot(np.arange(sz), rate60, color='r', label="Actual Hourly Rate",
            lw=3.5, zorder=3)

    # Find max rate
    maxi = np.argmax(rate1)
    maxwindow = 0
    maxwindowi = 0
    for i in range(maxi-10, maxi+1):
        if (prec[i+10] - prec[i]) > maxwindow:
            maxwindow = prec[i+10] - prec[i]
            maxwindowi = i

    print("MaxI: %s, rate: %s, window: %s-%s" % (maxi, rate1[maxi], maxwindowi,
                                                 maxwindowi+10))

    x = 0.1
    y = 0.9
    ax.text(x, y, "Peak 10min Window", transform=ax.transAxes,
            bbox=dict(fc='white', ec='None'))
    for i in range(maxwindowi+1, maxwindowi+11):
        ts = lsts + datetime.timedelta(minutes=i)
        ax.text(x, y - 0.045 - (0.04*(i-maxwindowi-1)),
                "%s %.2f" % (ts.strftime("%-I:%M %p"), prec[i] - prec[i-1], ),
                transform=ax.transAxes, fontsize=10,
                bbox=dict(fc='white', ec='None'))

    ax.set_xticks(xticks)
    ax.set_ylabel("Precipitation Rate [inch/hour]")
    ax.set_xticklabels(xlabels)
    ax.grid(True)
    print("xlim start is hard coded here, FYI")
    ax.set_xlim(60, sz)
    ax.legend(loc=(0.65, 0.84), prop=prop, ncol=1)
    ax.set_ylim(0, 8)
    ax.set_yticks(range(0, 9, 1))
    ax.set_xlabel("3-4 PM 17 July 2018 (EDT)")
    ax.set_title(("17 July 2018 Washington DC, Reagan National (DCA)\n"
                  "One Minute Rainfall, %.2f inches total plotted"
                  ) % (prec[-1],))

    fig.savefig('test.png')


if __name__ == '__main__':
    main()
