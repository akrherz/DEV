"""Fancy bar plot for feature fun"""
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

YEAR = """ 2013 |  0.145804676753783
 2014 |  0.150943396226415
 2015 |  0.126315789473684
 2016 |   0.12796697626419"""
YTD = """ 2013 |   0.12781954887218
 2014 |  0.144329896907216
 2015 |  0.152291105121294
 2016 |  0.107223476297968
 2017 | 0.073"""
YEARS = range(2013, 2018)
VALS = [float(line.split("|")[1].strip()) * 100. for line in YEAR.split("\n")]
VALS2 = [float(line.split("|")[1].strip()) * 100. for line in YTD.split("\n")]

FONT = FontProperties()
FONT.set_weight('bold')


def main():
    """Go"""
    plt.style.use('ggplot')
    ax = plt.axes([0.15, 0.15, 0.8, 0.7])
    ax.bar(YEARS[:-1], VALS, width=0.4, align='edge',
           label='Full Year')
    ax.bar(YEARS, VALS2, width=-0.4, align='edge',
           label='YTD to 24 May')
    for x, y in zip(YEARS, VALS):
        ax.text(x + 0.25, y + 0.5, "%.1f%%" % (y, ), ha='center',
                color='k', fontproperties=FONT)
    for x, y in zip(YEARS, VALS2):
        ax.text(x - 0.25, y + 0.5, "%.1f%%" % (y, ), ha='center',
                color='k', fontproperties=FONT)
    ax.set_ylim(0, 20)
    ax.set_xticks(YEARS)
    ax.legend(loc=(0.0, -0.15), ncol=2)
    plt.gcf().text(0.5, 0.93,
                   ("NWS Tornado Warning Issuance Tornado Tag\n"
                    "percentage of warnings indicating Tornado was OBSERVED\n"
                    "warnings without 'TORNADO...' tags were omitted"
                    ), fontsize=14, ha='center', va='center')
    plt.gcf().text(0.5, 0.01,
                   "* based on unofficial IEM, 24 May 2017, participating WFOs/Regions have changed",
                   ha='center')
    ax.set_ylabel("Percentage of Warnings")
    plt.gcf().savefig('test.png')


if __name__ == '__main__':
    main()
