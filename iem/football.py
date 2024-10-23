"""Unsure."""

import datetime
from io import StringIO

import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator as mlocator
from pyiem.database import get_dbconn
from pyiem.plot import figure_axes

data = """2002-09-14 17:05 I I
2003-09-13 11:30 S I
2004-09-11 11:05 I I
2005-09-10 14:30 S S
2006-09-16 11:00 I I
2007-09-15 12:30 S S
2008-09-13 11:00 I I
2009-09-12 11:00 S I
2010-09-11 14:30 I I
2011-09-10 11:00 S S
2012-09-08 14:42 I S
2013-09-14 17:00 S I
2014-09-13 15:30 I S
2015-09-12 15:45 S I
2016-09-10 18:42 I I
2017-09-09 11:01 S I
2018-09-08 16:05 I I
2019-09-14 15:11 S I
2021-09-11 15:37 S I
2022-09-10 15:05 I S
2023-09-09 14:41 S I
"""


def main():
    """Go Main Go."""
    games = pd.read_csv(
        StringIO(data),
        sep=" ",
        names=["date", "time", "location", "winner"],
    )
    games["valid"] = pd.to_datetime(games["date"] + " " + games["time"])
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()

    years = []
    tmpf = []
    sknt = []
    colors = []
    for _, row in games.iterrows():
        sts = row["valid"] - datetime.timedelta(hours=1)
        ets = row["valid"] + datetime.timedelta(minutes=30)
        station = "AMW" if row["location"] == "S" else "IOW"
        cursor.execute(
            """
        SELECT tmpf, sknt from alldata where station = %s
        and valid between %s and %s and report_type = 3 ORDER by valid DESC
        """,
            (station, sts, ets),
        )
        dbrow = cursor.fetchone()
        years.append(row["valid"].year)
        tmpf.append(dbrow[0])
        sknt.append(0 if dbrow[1] is None else (dbrow[1] * 1.15))
        colors.append("k" if row["winner"] == "I" else "#A71930")
    (fig, ax) = figure_axes(
        figsize=(8, 6),
        title="2002-2023 Iowa State vs Iowa Football Kickoff Weather",
        subtitle="Closest Ob in Time, Ames (AMW) or Iowa City (IOW)",
    )
    bars = ax.barh(np.array(years), tmpf, align="center")
    irec = None
    srec = None
    for i, bar in enumerate(bars):
        bar.set_facecolor(colors[i])
        if colors[i] == "k":
            irec = bar
        else:
            srec = bar
        ax.text(tmpf[i] + 1, years[i], "%.0f" % (tmpf[i],), va="center")
    n90 = [100] * len(years)
    bars = ax.barh(np.array(years), sknt, left=n90, align="center")
    for i, bar in enumerate(bars):
        bar.set_facecolor(colors[i])
        ax.text(sknt[i] + 101, years[i], "%.0f" % (sknt[i],), va="center")
    ax.set_xticks([55, 60, 65, 70, 75, 80, 85, 90, 100, 105, 110, 115, 120])
    ax.set_xticklabels([55, 60, 65, 70, 75, 80, 85, 90, 0, 5, 10, 15, 20])
    ax.set_xlabel(
        "Air Temperature [F]                          Wind Speed [mph]"
    )
    ax.set_xlim(55, 125)
    ax.grid(True)
    ax.legend((irec, srec), ("Iowa Won", "Iowa State Won"), ncol=2)
    ax.set_ylim(2001.5, 2025.5)
    ax.yaxis.set_major_locator(mlocator(integer=True))

    fig.savefig("240906.png")


if __name__ == "__main__":
    main()
