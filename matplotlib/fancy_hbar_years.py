"""Fancy bar plot for feature fun"""

import datetime

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

DATES = """ 1997 | 1997-01-04
 1998 | 1998-01-14
 1999 | 1999-01-01
 2000 | 2000-01-02
 2001 | 2001-01-19
 2002 | 2002-01-02
 2003 | 2003-02-14
 2004 | 2004-01-24
 2005 | 2005-01-07
 2006 | 2006-01-01
 2007 | 2007-01-04
 2008 | 2008-01-07
 2009 | 2009-01-03
 2010 | 2010-01-20
 2011 | 2010-12-31
 2012 | 2012-01-16
 2013 | 2013-01-10
 2014 | 2014-01-11
 2015 | 2015-01-03
 2016 | 2016-01-08
 2017 | 2017-01-02
 2018 | 2018-01-21
 2019 | 2019-01-19
 2020 | 2020-01-10"""

YEARS = []
VALS = []
LABELS = []
for line in DATES.split("\n"):
    tokens = line.split("|")
    ts = datetime.datetime.strptime(tokens[1].strip(), "%Y-%m-%d")
    YEARS.append(int(tokens[0]))
    if YEARS[-1] == 2011:
        VALS.append(0)
        LABELS.append(ts.strftime("%b %-d %Y") + "(2011)")
    else:
        VALS.append(int(ts.strftime("%j")))
        LABELS.append(ts.strftime("%b %-d %Y"))
FONT = FontProperties()
FONT.set_weight("bold")


def main():
    """Go"""
    plt.style.use("ggplot")
    ax = plt.axes([0.3, 0.1, 0.65, 0.8])
    ax.barh(YEARS, VALS)
    # for y, x in enumerate(YEARS):
    #    ax.text(VALS[y] + 5, x, "%s" % (labels[y], ), va='center', ha='left',
    #            color='k', fontproperties=FONT)
    ax.set_xticks((1, 15, 32, 47))
    ax.set_xticklabels(["1 Jan", "15 Jan", "1 Feb", "15 Feb"])
    ax.set_yticks(YEARS)
    ax.set_xlim(0, max(VALS) + 10)
    ax.set_yticklabels(LABELS)
    avgval = int(np.mean(np.array(VALS))) - 1
    ax.axvline(avgval + 1, lw=2, color="k")
    avgdate = datetime.date(2020, 1, 1) + datetime.timedelta(days=avgval)
    ax.text(avgval + 2, 2020, "Avg: %s" % (avgdate.strftime("%-d %b")))
    plt.gcf().text(
        0.5,
        0.93,
        ("1997-2020 Date (Central Time) of SPC Watch Number 1\n"),
        fontsize=14,
        ha="center",
        va="center",
    )
    plt.gcf().text(
        0.5,
        0.01,
        "* based on unofficial archives maintained by the IEM, 10 Jan 2020",
        ha="center",
    )
    plt.gcf().savefig("test.png")


if __name__ == "__main__":
    main()
