"""Fancy bar plot for feature fun"""
import datetime

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

DATA = """  2018-02-21 |   269
 2001-12-05 |   252
 2002-04-16 |   229
 2015-12-24 |   226
 2012-03-19 |   217
 2015-12-14 |   208
 2012-03-18 |   203
 2012-03-20 |   203
 2015-12-27 |   203
 2018-02-20 |   202"""

FONT = FontProperties()
FONT.set_weight('bold')


def main():
    """Go"""
    plt.style.use('ggplot')
    ax = plt.axes([0.2, 0.15, 0.75, 0.7])

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
                   ("Number of NWS Issued Record Event Reports (RER)\n"
                    "by calendar date (US Central Time Zone) [2001-2018]"
                    ), fontsize=14, ha='center', va='center')
    plt.gcf().text(0.5, 0.01,
                   ("* based on unofficial archives maintained by the IEM, "
                    "thru 21 Feb 2018, @akrherz"),
                   ha='center')
    ax.set_xlabel("Number of Record Event Reports")
    ax.set_yticks(range(len(vals)))
    ax.set_yticklabels(ylabels)
    plt.gcf().savefig('test.png')


if __name__ == '__main__':
    main()
