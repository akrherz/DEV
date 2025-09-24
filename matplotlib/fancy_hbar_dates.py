"""Fancy bar plot for feature fun"""

import numpy as np
from matplotlib.font_manager import FontProperties
from pyiem.plot import figure

DATA = """OUN - Norman, OK |      2025 |  1121
OUN - Norman, OK  |      2024 |   988
FFC - Atlanta, GA |      1998 |   956
OUN - Norman, OK |      2019 |   942
OUN - Norman, OK |      2017 |   923
OUN - Norman, OK |      2016 |   907
OUN - Norman, OK |      2023 |   894
LZK - Little Rock, AR |      2011 |   888
OUN - Norman, OK |      2008 |   871
JAN - Jackson, MS |      2001 |   848
SKIP
FSD - Sioux Falls, SD |      2004 |   548
DMX - Des Moines, IA |      2008 |   509
OAX - Omaha, NE |      2001 |   469
DVN - Davenport, IA |      2024 |   364
ARX - La Crosse, WI |      1998 |   241"""

FONT = FontProperties()
FONT.set_weight("bold")
FONT.set_size("large")


def main():
    """Go"""
    fig = figure(
        title=(
            "Largest Yearly Severe Thunderstorm Warning Totals [1986-]"
            "\nby NWS Forecast Office"
        ),
        figsize=(10.24, 7.68),
    )
    ax = fig.add_axes((0.4, 0.15, 0.55, 0.7))

    ylabels = []
    vals = []
    for line in DATA.split("\n"):
        if line.strip() == "SKIP":
            ylabels.append("-- Max for Iowa Forecast Offices --")
            vals.append(np.nan)
            continue
        tokens = line.strip().split("|")
        vals.append(int(tokens[2]))
        ylabels.append(f"{tokens[0]} | {tokens[1].strip()}")

    vals = vals[::-1]
    ylabels = ylabels[::-1]

    ax.barh(range(len(vals)), vals)
    for y, x in enumerate(vals):
        if not np.isnan(x):  # Skip text for NaN values
            # Simple white text that's easy to read
            ax.text(
                x - 2,
                y,
                f"{x:,}",  # Add comma formatting
                va="center",
                ha="right",
                color="white",
                fontproperties=FONT,
                fontsize=14,
            )
    fig.text(
        0.5,
        0.03,
        ("* thru 23 September 2025, unofficial IEM accounting."),
        ha="center",
    )
    ax.set_xlabel("Number of Warnings")
    ax.set_yticks(range(len(vals)))
    ax.set_yticklabels(ylabels, fontsize=14)

    # Clean up the axes presentation
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.5)
    ax.spines["bottom"].set_linewidth(0.5)

    # Style the ticks
    ax.tick_params(axis="x", which="major", labelsize=12, length=4, width=0.5)
    ax.tick_params(axis="y", which="major", labelsize=14, length=0, width=0)

    # Add subtle grid for x-axis only
    ax.grid(axis="x", alpha=0.3, linestyle="-", linewidth=0.5)
    ax.set_axisbelow(True)

    fig.savefig("250924.png")


if __name__ == "__main__":
    main()
