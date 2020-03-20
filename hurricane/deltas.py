"""Plot things"""
import datetime

import numpy as np
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt


def main():
    """Go Main Go"""
    pgconn = get_dbconn("coop")
    df = read_sql(
        """
    select sday, to_char(day, 'YYYYMMDD') as date, high, low, precip
    from alldata_ia
    where station = 'IA2203'
    """,
        pgconn,
        index_col="date",
    )
    climo = df.groupby("sday").mean()

    hevents = []
    levents = []
    pevents = []
    for line in open("dates.txt"):
        date = line.strip()
        if date not in df.index:
            continue
        dt = datetime.datetime.strptime(date, "%Y%m%d")
        harr = []
        larr = []
        parr = []
        for dy in range(-5, 6):
            dt2 = dt + datetime.timedelta(days=dy)
            deltahigh = (
                df.at[dt2.strftime("%Y%m%d"), "high"]
                - climo.at[dt2.strftime("%m%d"), "high"]
            )
            harr.append(deltahigh)
            deltalow = (
                df.at[dt2.strftime("%Y%m%d"), "low"]
                - climo.at[dt2.strftime("%m%d"), "low"]
            )
            larr.append(deltalow)
            parr.append(
                1 if df.at[dt2.strftime("%Y%m%d"), "precip"] >= 0.01 else 0
            )
        hevents.append(harr)
        levents.append(larr)
        pevents.append(parr)

    hdata = np.array(hevents)
    highs = np.mean(hdata, axis=0)
    ldata = np.array(levents)
    lows = np.mean(ldata, axis=0)
    pdata = np.array(pevents)
    precip = np.mean(pdata, axis=0)

    (fig, ax) = plt.subplots(3, 1, sharex=True)
    fig.text(
        0.1,
        0.95,
        (
            "Des Moines Daily Weather (1880-2017)\n"
            "for dates around US East Coast Landfalling Hurricane"
        ),
        ha="left",
        va="center",
        fontsize=14,
    )
    ax[0].text(
        0.02, 1.02, "High Temperature Departure", transform=ax[0].transAxes
    )
    ax[0].grid(True)
    ax[0].set_ylabel(r"Departure $^\circ$F")
    ax[0].set_ylim(-3, 3)
    ax[0].set_yticks(range(-2, 3))
    bars = ax[0].bar(np.arange(-5, 6), highs)
    for i, _bar in enumerate(bars):
        if highs[i] > 0:
            _bar.set_color("r")

    ax[1].text(
        0.02, 1.02, "Low Temperature Departure", transform=ax[1].transAxes
    )
    ax[1].grid(True)
    ax[1].set_ylabel(r"Departure $^\circ$F")
    ax[1].set_yticks(range(-2, 3))
    ax[1].set_ylim(-3, 3)
    bars = ax[1].bar(np.arange(-5, 6), lows)
    for i, _bar in enumerate(bars):
        if lows[i] > 0:
            _bar.set_color("r")

    ax[2].bar(np.arange(-5, 6), precip * 100.0)
    ax[2].text(
        0.02, 1.02, "Measurable Rainfall Frequency", transform=ax[2].transAxes
    )
    ax[2].set_ylim(bottom=0)
    ax[2].set_ylabel("Frequency [%]")
    ax[2].grid(True)
    ax[2].set_xlabel(
        ("Relative Days to Hurricane Landfall, " "%s events considered")
        % (len(hevents),)
    )

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
