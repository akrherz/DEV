"""Fancy bar plot for feature fun"""
import datetime

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

DATA = """ 2017-09-10 |    48
 2008-08-19 |    15
 2007-02-02 |    12
 1998-09-25 |    11
 2004-08-13 |    11
 2010-03-11 |    11
 1997-04-28 |    10
 2013-06-06 |    10"""

FONT = FontProperties()
FONT.set_weight('bold')


def main():
    """Go"""
    plt.style.use('ggplot')
    ax = plt.axes([0.3, 0.15, 0.65, 0.7])

    ylabels = []
    vals = []
    for line in DATA.split("\n"):
        tokens = line.strip().split("|")
        vals.append(int(tokens[1]))
        ts = datetime.datetime.strptime(tokens[0].strip(),
                                        '%Y-%m-%d')
        ylabels.append(ts.strftime("%b %d, %Y"))

    vals = vals[::-1]
    ylabels = ylabels[::-1]

    ax.barh(range(len(vals)), vals)
    for y, x in enumerate(vals):
        ax.text(x - 2, y, "%s" % (x, ), va='center', ha='right',
                color='yellow', fontproperties=FONT)
    plt.gcf().text(0.5, 0.93,
                   ("Largest Number of NWS Melbourne Tornado Warnings Issued\n"
                    "for One Calendar Day (US Eastern Time Zone) [1996-2017]"
                    ), fontsize=14, ha='center', va='center')
    plt.gcf().text(0.5, 0.01,
                   ("* based on unofficial archives maintained by the IEM, "
                    "thru 10 Sep 2017, @akrherz"),
                   ha='center')
    ax.set_xlabel("Number of Tornado Warnings")
    ax.set_yticks(range(len(vals)))
    ax.set_yticklabels(ylabels)
    plt.gcf().savefig('test.png')


if __name__ == '__main__':
    main()
