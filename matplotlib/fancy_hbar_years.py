"""Fancy bar plot for feature fun"""
import calendar
import datetime

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

DATES = """1997-04-05 15:00:00+00
1998-03-30 21:15:00+00
1999-04-08 05:00:00+00
2000-04-03 18:30:00+00
2001-05-06 19:45:00+00
2002-05-06 00:30:00+00
2003-04-25 04:45:00+00
2004-05-22 02:55:00+00
2005-05-11 19:55:00+00
2006-03-31 20:45:00+00
2007-03-31 22:15:00+00
2008-03-08 11:15:00+00
2009-04-05 22:05:00+00
2010-05-01 05:00:00+00
2011-04-11 00:30:00+00
2012-04-12 18:50:00+00
2013-04-27 20:50:00+00
2014-05-11 19:40:00+00
2015-05-11 04:30:00+00
2016-05-26 18:05:00+00
2017-04-21 21:40:00+00
2018-08-27 00:35:00+00"""

YEARS = []
VALS = []
LABELS = []
for line in DATES.split("\n"):
    ts = datetime.datetime.strptime(line[:10], '%Y-%m-%d')
    YEARS.append(ts.year)
    VALS.append(int(ts.strftime("%j")))
    LABELS.append(ts.strftime("%b %-d %Y"))
FONT = FontProperties()
FONT.set_weight('bold')


def main():
    """Go"""
    plt.style.use('ggplot')
    ax = plt.axes([0.3, 0.1, 0.65, 0.8])
    ax.barh(YEARS, VALS)
    #for y, x in enumerate(YEARS):
    #    ax.text(VALS[y] + 5, x, "%s" % (labels[y], ), va='center', ha='left',
    #            color='k', fontproperties=FONT)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335,
                   365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_yticks(YEARS)
    ax.set_xlim(0, VALS[-1] + 10)
    ax.set_yticklabels(LABELS)
    plt.gcf().text(0.5, 0.93,
                   ("1997-2018 Date of 75th SPC Tornado Watch\n"
                    ), fontsize=14, ha='center', va='center')
    plt.gcf().text(0.5, 0.01,
                   "* based on unofficial archives maintained by the IEM, 31 Aug 2018",
                   ha='center')
    plt.gcf().savefig('test.png')


if __name__ == '__main__':
    main()
