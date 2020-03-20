"""Fancy bar plot for feature fun"""
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

XLABELS = [
    "Tornado",
    "Flash Flood",
    "Winter Storm",
    "Severe Thunderstorm",
    "Blizzard",
    "High Wind",
]
VALS = [55, 59, 69, 73, 85, 86]
VALS2 = [16, 19, 51, 35, 74, 80]
FONT = FontProperties()
FONT.set_weight("bold")


def main():
    """Go"""
    plt.style.use("ggplot")
    ax = plt.axes([0.3, 0.15, 0.65, 0.7])
    ax.barh(
        range(len(VALS)), VALS, height=0.4, align="edge", label="Per Watch"
    )
    ax.barh(
        range(len(VALS)),
        VALS2,
        height=-0.4,
        align="edge",
        label="Per County/Zone in Watch",
    )
    for y, x in enumerate(VALS):
        ax.text(
            x - 2,
            y + 0.2,
            "%s%%" % (x,),
            va="center",
            ha="right",
            color="yellow",
            fontproperties=FONT,
        )
    for y, x in enumerate(VALS2):
        ax.text(
            x - 2,
            y - 0.2,
            "%s%%" % (x,),
            va="center",
            ha="right",
            color="yellow",
            fontproperties=FONT,
        )
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 25))
    ax.legend(loc=(0.0, -0.15), ncol=2)
    plt.gcf().text(
        0.5,
        0.93,
        (
            "NWS Des Moines 2007-2016\n"
            "percentage of watches that receive 1+ warning\n"
            "values are for straight conversions, not higher end warnings"
        ),
        fontsize=14,
        ha="center",
        va="center",
    )
    plt.gcf().text(
        0.5,
        0.01,
        "* based on unofficial archives maintained by the IEM, 10 May 2017",
        ha="center",
    )
    ax.set_yticks(range(len(VALS)))
    ax.set_yticklabels(XLABELS)
    plt.gcf().savefig("test.png")


if __name__ == "__main__":
    main()
