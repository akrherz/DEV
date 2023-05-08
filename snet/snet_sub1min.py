"""Plot sub-minute data"""
import datetime

import numpy as np

import matplotlib.font_manager
import matplotlib.pyplot as plt
from pyiem.datatypes import humidity, temperature
from pyiem.meteorology import dewpoint

txt2drct = {
    "N": "360",
    "North": "360",
    "NNE": "25",
    "NE": "45",
    "ENE": "70",
    "E": "90",
    "East": "90",
    "ESE": "115",
    "SE": "135",
    "SSE": "155",
    "S": "180",
    "South": "180",
    "SSW": "205",
    "SW": "225",
    "WSW": "250",
    "W": "270",
    "West": "270",
    "WNW": "295",
    "NW": "315",
    "NNW": "335",
}


def main():
    """Go Main Go"""
    valid = []
    pres = []
    sped = []
    drct = []
    tmpf = []
    dwpf = []
    pday = []
    lines = []
    now = datetime.datetime(2018, 4, 13, 0, 0)

    for line in open("jefferson.txt", encoding="utf8"):
        if line.find("Min") > 0 or line.find("Max") > 0:
            continue
        ts = datetime.datetime.strptime(line[7:21], "%H:%M %m/%d/%y")
        if len(lines) == 0:
            now = ts
        if ts == now:
            lines.append(line)
            continue
        # Spread obs
        now = ts
        delta = 60.0 / len(lines)
        for line in lines:
            ts += datetime.timedelta(seconds=delta)
            t = float(line[42:45])
            rhval = float(line[47:50])
            tmpf.append(t)
            dwpf.append(
                dewpoint(temperature(t, "F"), humidity(rhval, "%")).value("F")
            )
            pres.append(float(line[52:57]) * 33.86375)
            sped.append(float(line[26:28]))
            pday.append(float(line[59:64]))
            drct.append(float(txt2drct[line[22:25].strip()]) - 20.0)
            # Clock was not in CDT
            valid.append(ts + datetime.timedelta(minutes=60))
        lines = []

    sts = datetime.datetime(2018, 4, 13, 17, 0)
    ets = datetime.datetime(2018, 4, 13, 18, 0)
    interval = datetime.timedelta(minutes=15)
    xticks = []
    xticklabels = []
    now = sts
    while now < ets:
        fmt = ":%M"
        if now.minute == 0 or not xticks:
            fmt = "%-I:%M %p"
        xticks.append(now)
        xticklabels.append(now.strftime(fmt))

        now += interval

    fig, ax = plt.subplots(3, 1, sharex=True)

    """
    fancybox = mpatches.FancyBboxPatch(
            [mx.DateTime.DateTime(2012,5,3,8,6).ticks(),
            40], 60*18, 50,
            boxstyle='round', alpha=0.2, facecolor='#7EE5DE',
            edgecolor='#EEEEEE',
            zorder=1)
    ax[0].add_patch( fancybox)
    """
    ax[0].plot(valid, np.array(tmpf), label="Air")
    # print("%s %s" % (tmpf, max(tmpf)))
    ax[0].plot(valid, np.array(dwpf), color="g", label="Dew Point")
    # ax[0].set_ylim(40, 92)
    ax[1].scatter(valid, drct, zorder=2)
    ax2 = ax[1].twinx()
    ax2.plot(valid, sped, "r")
    ax2.set_ylabel("Wind Speed [mph]")

    ax[2].plot(valid, pres, "b", label="Pressure [mb]")
    ax[2].set_ylim(1006, 1014)
    # ax3 = ax[2].twinx()
    # ax3.plot(valid, pday, 'r')
    # ax3.set_ylabel("Daily Precip [inch]")

    ax[0].set_xticks(xticks)
    ax[0].set_xticklabels(xticklabels)
    ax[0].set_xlim(sts, ets)
    prop = matplotlib.font_manager.FontProperties(size=12)

    ax[0].legend(loc=2, prop=prop, ncol=2)
    ax[2].legend(loc=1, prop=prop)
    ax[0].grid(True)
    ax[1].grid(True)
    ax[2].grid(True)
    ax[0].set_title("Jefferson SchoolNet8 Site (~ $\Delta$6 second data)")
    ax[2].set_xlabel("Afternoon of 13 Apr 2018")
    # ax[2].set_ylabel("Pressure [mb]")
    # [t.set_color('red') for t in ax3.yaxis.get_ticklines()]
    # [t.set_color('red') for t in ax3.yaxis.get_ticklabels()]
    [t.set_color("red") for t in ax2.yaxis.get_ticklines()]
    [t.set_color("red") for t in ax2.yaxis.get_ticklabels()]
    [t.set_color("b") for t in ax[2].yaxis.get_ticklines()]
    [t.set_color("b") for t in ax[2].yaxis.get_ticklabels()]
    # [t.set_color('b') for t in ax[0].yaxis.get_ticklines()]
    # [t.set_color('b') for t in ax[0].yaxis.get_ticklabels()]
    [t.set_color("b") for t in ax[1].yaxis.get_ticklines()]
    [t.set_color("b") for t in ax[1].yaxis.get_ticklabels()]
    ax[1].set_ylabel("Wind Direction")
    ax[0].set_ylabel(r"Temperature $^{\circ}\mathrm{F}$")
    ax[1].set_yticks(np.arange(0, 361, 90))
    ax[1].set_ylim(0, 361)
    ax[1].set_yticklabels(["N", "E", "S", "W", "N"])
    ax[2].set_ylim(min(pres) - 2, max(pres) + 4)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
