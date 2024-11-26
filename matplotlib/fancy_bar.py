"""Fancy bar plot for feature fun"""

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

YEAR = """ 2002 | 4.4847571658840844
 2003 | 4.8973395657682058
 2004 | 5.4299534807130213
 2005 | 5.6124545796266132
 2006 | 5.7710470006640596
 2007 | 5.8854634801965643
 2008 | 7.6544413890132378
 2009 | 7.7650388365559412
 2010 | 7.7160190985150467
 2011 | 8.3703411036480969
 2012 | 8.1527753226091568
 2013 | 7.9481497418244406
 2014 | 7.9322700458815818
 2015 | 8.0290087463556851
 2016 | 7.9291307752545027
 2017 | 8.0270724421209858
 2018 | 7.7885044642857143"""
YTD = """ 2013 |   0.12781954887218
 2014 |  0.144329896907216
 2015 |  0.152291105121294
 2016 |  0.107223476297968
 2017 | 0.073"""
YEARS = range(2002, 2019)
VALS = [float(line.split("|")[1].strip()) for line in YEAR.split("\n")]
VALS2 = [float(line.split("|")[1].strip()) * 100.0 for line in YTD.split("\n")]

FONT = FontProperties()
FONT.set_weight("bold")


def main():
    """Go"""
    plt.style.use("ggplot")
    ax = plt.axes([0.1, 0.15, 0.87, 0.7])
    ax.bar(YEARS, VALS, width=0.4, align="center", label="Full Year")
    # ax.bar(YEARS, VALS2, width=-0.4, align='edge',
    #       label='YTD to 24 May')
    for x, y in zip(YEARS, VALS, strict=False):
        ax.text(
            x,
            y + 0.5,
            "%.1f" % (y,),
            ha="center",
            color="k",
            fontproperties=FONT,
        )
    # for x, y in zip(YEARS, VALS2):
    #    ax.text(x - 0.25, y + 0.5, "%.1f%%" % (y, ), ha='center',
    #            color='k', fontproperties=FONT)
    ax.set_ylim(0, 10)
    ax.set_xticks(YEARS[::2])
    # ax.legend(loc=(0.0, -0.15), ncol=2)
    plt.gcf().text(
        0.5,
        0.93,
        (
            "NWS Severe TStorm + Tornado Warning Polygon\n"
            "average number of polygon vertices per warning by year\n"
            "polygons prior to October 2007 were unofficial"
        ),
        fontsize=14,
        ha="center",
        va="center",
    )
    plt.gcf().text(
        0.5,
        0.01,
        "* based on unofficial IEM data, 15 Mar 2019, @akrherz",
        ha="center",
    )
    ax.set_ylabel("Average Number of Polygon Vertices")
    plt.gcf().savefig("test.png")


if __name__ == "__main__":
    main()
