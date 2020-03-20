"""Create a pretty table."""

import numpy as np
from pyiem.plot.use_agg import plt
import seaborn as sns
import matplotlib.colors as mpcolors
from matplotlib.font_manager import FontProperties
from matplotlib import patches
from metpy.calc import heat_index, relative_humidity_from_dewpoint
from metpy.units import units
from metpy.plots import add_metpy_logo

COLORS = ["#ffff02", "#ffcc00", "#fe6500", "#cc0001"]
LEVELS = [0, 91, 103, 126, 200]
LABELS = ["Caution", "Extreme Caution", "Danger", "Extreme Danger"]
LEGENDLOCS = [0.15, 0.3, 0.6, 0.75]


def main():
    """Go Main Go."""
    titlefont = FontProperties()
    titlefont.set_weight("bold")
    titlefont.set_size(24)

    lblfont = titlefont.copy()
    lblfont.set_size(15)

    dwpf1d = np.arange(40, 90, 2)
    tmpf1d = np.arange(80, 131, 2)
    tmpf, dwpf = np.meshgrid(tmpf1d, dwpf1d)
    rh = relative_humidity_from_dewpoint(tmpf * units.degF, dwpf * units.degF)
    hi = heat_index(tmpf * units.degF, rh)
    hi[hi > 137.5 * units.degF] = np.nan
    fig = plt.Figure(figsize=(12.48 * 1.2, 7.44 * 1.2))

    faux = fig.add_axes([0, 0, 1, 1])
    faux.xaxis.set_visible(False)
    faux.yaxis.set_visible(False)
    ax = fig.add_axes([0.11, 0.15, 0.86, 0.7])

    rect = patches.Rectangle(
        (0.02, 0.017),
        0.963,
        0.964,
        linewidth=2,
        edgecolor="k",
        facecolor="none",
    )
    faux.add_patch(rect)
    rect = patches.Rectangle(
        (0.11, 0.15), 0.86, 0.7, linewidth=3, edgecolor="k", facecolor="none"
    )
    faux.add_patch(rect)

    rect = patches.Rectangle(
        (0.06, 0.15), 0.91, 0.76, linewidth=3, edgecolor="k", facecolor="none"
    )
    faux.add_patch(rect)

    for color, label, loc in zip(COLORS, LABELS, LEGENDLOCS):
        rect = patches.Rectangle(
            (loc, 0.055),
            0.02,
            0.02,
            linewidth=1,
            edgecolor="k",
            facecolor=color,
        )
        faux.add_patch(rect)
        fig.text(
            loc + 0.03,
            0.06,
            label,
            va="center",
            ha="left",
            fontproperties=lblfont,
        )

    fig.text(
        0.06,
        0.93,
        "NWS Heat Index",
        color="blue",
        ha="left",
        fontproperties=titlefont,
    )
    fig.text(
        0.5,
        0.1,
        (
            "Likelihood of Heat Disorders with Prolonged Exposure or "
            "Strenuous Activity"
        ),
        ha="center",
        fontproperties=lblfont,
    )
    cmap = mpcolors.ListedColormap(COLORS, "")
    cmap.set_bad(COLORS[-1])
    norm = mpcolors.BoundaryNorm(LEVELS, cmap.N)
    sns.heatmap(
        hi,
        annot=True,
        fmt=".0f",
        linewidths=0,
        ax=ax,
        cmap=cmap,
        norm=norm,
        xticklabels=[str(x) for x in tmpf1d],
        yticklabels=[str(x) for x in dwpf1d],
        cbar=False,
        annot_kws=dict(color="k", fontsize=16),
    )
    ax.set_ylim(len(dwpf1d), 0)
    ax.set_xlim(0, len(tmpf1d))
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.tick_params(axis="both", which="both", length=0)
    ax.set_ylabel(
        r"Dew Point Temperature ($^\circ$F)",
        fontproperties=lblfont,
        labelpad=15 * 1.8,
    )
    ax.set_xlabel(
        r"Temperature ($^\circ$F)", fontproperties=lblfont, labelpad=20 * 1.2
    )
    plt.setp(
        ax.yaxis.get_majorticklabels(), rotation=0, fontproperties=lblfont
    )
    plt.setp(
        ax.xaxis.get_majorticklabels(), rotation=0, fontproperties=lblfont
    )
    # add_metpy_logo(fig, 1290, 150, size='large')

    for x in range(5, 25, 5):
        ax.axhline(x, color="k")

    fig.savefig("test.png")  # , orientation='horizontal')


if __name__ == "__main__":
    main()
