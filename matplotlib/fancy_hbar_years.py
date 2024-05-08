"""Fancy bar plot for feature fun"""

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

DATES = """ 2011 |     9
 2006 |     5
 2005 |     5
 2003 |     5
 1998 |     5
 2024 |     4
 2008 |     4
 2004 |     4
 1999 |     4"""

YEARS = []
VALS = []
LABELS = []
for line in DATES.split("\n"):
    tokens = line.split("|")
    YEARS.append(int(tokens[0]))
    VALS.append(int(tokens[1]))
FONT = FontProperties()
FONT.set_weight("bold")


def main():
    """Go"""
    plt.style.use("ggplot")
    ax = plt.axes([0.2, 0.1, 0.65, 0.75])
    ax.barh(range(0, len(YEARS)), VALS)
    for y, val in enumerate(VALS):
        ax.text(
            val - 0.5,
            y,
            f"{val}",
            va="center",
            ha="left",
            color="white",
            fontproperties=FONT,
        )
    ax.set_xticks((1, 5, 10))
    ax.set_yticks(range(0, len(YEARS)))
    ax.set_xlim(0, 10)
    ax.set_yticklabels([str(x) for x in YEARS])
    plt.gcf().text(
        0.5,
        0.93,
        (
            "Number of Days (US Central TZ)\n"
            "with 100+ Tornado Warnings Issued (1986-2024)"
        ),
        fontsize=14,
        ha="center",
        va="center",
    )
    plt.gcf().text(
        0.5,
        0.01,
        "* based on unofficial archives maintained by the IEM, 7 May 2024",
        ha="center",
    )
    plt.gcf().savefig("test.png")


if __name__ == "__main__":
    main()
