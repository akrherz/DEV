"""Fancy bar plot for feature fun"""

import datetime

from matplotlib.font_manager import FontProperties
from pyiem.plot import figure, plt

DATA = """   2011-04-27 |   450
 2012-03-02 |   285
 2004-05-30 |   283
 2011-05-25 |   282
 2011-04-26 |   274
 2010-10-26 |   222
 2023-03-31 |   215
 2008-02-05 |   211
 2006-04-07 |   198
 2011-04-15 |   194"""

FONT = FontProperties()
FONT.set_weight("bold")
FONT.set_size("large")


def main():
    """Go"""
    plt.style.use("ggplot")
    fig = figure(
        title=(
            "Top 10 Number of NWS Issued Tornado Warnings\n"
            "by 'convective day' (~7AM - 7AM CDT), "
            "date shown for start of period [2002-]"
        ),
        figsize=(10.24, 7.68),
    )
    ax = fig.add_axes([0.2, 0.15, 0.75, 0.7])

    ylabels = []
    vals = []
    colors = []
    for line in DATA.split("\n"):
        tokens = line.strip().split("|")
        vals.append(int(tokens[1]))
        ts = datetime.datetime.strptime(tokens[0].strip(), "%Y-%m-%d")
        colors.append("r" if ts.year == 2023 else "tan")
        ylabels.append(ts.strftime("%b %d, %Y"))

    vals = vals[::-1]
    ylabels = ylabels[::-1]
    colors = colors[::-1]

    ax.barh(range(len(vals)), vals, color=colors)
    for y, x in enumerate(vals):
        ax.text(
            x - 2,
            y,
            f"{x}",
            va="center",
            ha="right",
            color="k",
            fontproperties=FONT,
        )
    fig.text(
        0.5,
        0.03,
        (
            "* based on unofficial archives maintained by the IEM, "
            "thru 31 March 2023, @akrherz"
        ),
        ha="center",
    )
    ax.set_xlabel("Number of Warnings")
    ax.set_yticks(range(len(vals)))
    ax.set_yticklabels(ylabels, fontsize=14)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
