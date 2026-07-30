"""Le Sigh, again"""

from zoneinfo import ZoneInfo

import pandas as pd
from matplotlib.lines import Line2D
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable
from pyiem.plot import figure

CST = ZoneInfo("America/Chicago")


def main():
    """Go Main Go."""
    nt = NetworkTable("IA_ASOS")
    # meh
    federal_asos = (
        "AMW DSM ALO DBQ CID IOW EST SPW SUX OTM BRL MCW MIW DVN LWD"
    ).split()
    federal_awos = ["FOD", "CWI"]
    with get_sqlalchemy_conn("asos") as conn:
        statsdf = pd.read_sql(
            sql_helper("""
            select station, count(*),
    sum(case when relh = 100 then 1 else 0 end) / count(*)::numeric * 100.
    as freq,
    sum(case when relh is null then 1 else 0 end) / count(*)::numeric * 100.
    as nodata,
    sum(case when extract(hour from valid) between 12 and 20 and relh > 90
        then 1 else 0 end) /
    sum(case when extract(hour from valid) between 12 and 20
        then 1 else 0 end)::numeric * 100. as afternoon_rh90,
    max(dwpf), avg(dwpf) from t2026 t JOIN stations s on
    (t.station = s.id and s.network = 'IA_ASOS')
    where valid > '2026-07-25' and valid < '2026-07-30'
    and report_type in (3, 4)
    GROUP by station order by freq desc;
            """),
            conn,
            index_col="station",
        )
    # Require nodata less than 5%
    statsdf = statsdf[statsdf["nodata"] < 5]
    statsdf["color"] = "b"
    statsdf.loc[statsdf.index.isin(federal_asos), "color"] = "r"
    statsdf.loc[statsdf.index.isin(federal_awos), "color"] = "g"

    fig = figure(
        figsize=(9, 10),
    )
    fig.text(
        0.5,
        0.99,
        (
            "25-29 July 2026: Iowa Airport Humidity Metrics\n"
            "Only Stations with <5% Missing, Sorted by Freq of 100% RH"
        ),
        ha="center",
        va="top",
        fontsize=16,
    )
    y0 = 0.08
    x0 = 0.20
    xwidth = 0.16
    yheight = 0.81

    # Create axes with only left size and bottom splines visible
    ax = fig.add_axes((x0, y0, xwidth, yheight))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.barh(
        statsdf.index.values,
        statsdf["freq"].values,
        color=statsdf["color"].values,
    )
    ax.set_xlabel("All Hours RH = 100%\nFrequency [%]")
    ax.set_yticks(list(range(len(statsdf.index.values))))
    ax.set_yticklabels(
        [f"{x} {nt.sts[x]['name']}" for x in statsdf.index.values]
    )
    # Color the yaxis labels using the same as the colorbars
    for i, label in enumerate(ax.get_yticklabels()):
        label.set_color(statsdf["color"].values[i])
    ax.set_ylim(-0.5, len(statsdf.index.values) - 0.5)

    # Label the bars with integer value
    for i, v in enumerate(statsdf["freq"].values):
        ax.text(
            v + 3,
            i,
            f"{v:.0f}",
            color=statsdf["color"].values[i],
            va="center",
        )

    # --------------------------------------
    ax2 = fig.add_axes((x0 + xwidth + 0.05, y0, xwidth, yheight))
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    ax2.barh(
        statsdf.index.values,
        statsdf["max"].values,
        color=statsdf["color"].values,
    )
    ax2.set_xticks([80, 85, 90])
    ax2.grid(axis="x")
    ax2.set_xlim(statsdf["max"].min() - 3, statsdf["max"].max() + 3)
    ax2.set_xlabel("Maximum\nDew Point °F")
    ax2.set_yticks([])
    ax2.set_ylim(*ax.get_ylim())
    # Label the bars with integer value
    for i, v in enumerate(statsdf["max"].values):
        ax2.text(
            v + 0.5,
            i,
            f"{v:.0f}",
            color=statsdf["color"].values[i],
            va="center",
        )

    # --------------------------------------
    ax3 = fig.add_axes((x0 + xwidth * 2 + 0.1, y0, xwidth, yheight))
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)

    ax3.barh(
        statsdf.index.values,
        statsdf["avg"].values,
        color=statsdf["color"].values,
    )
    ax3.set_xticks([65, 70, 75])
    ax3.grid(axis="x")
    ax3.set_xlim(statsdf["avg"].min() - 3, statsdf["avg"].max() + 3)
    ax3.set_xlabel("Average\nDew Point °F")
    ax3.set_yticks([])
    ax3.set_ylim(*ax.get_ylim())

    # Label the bars with integer value
    for i, v in enumerate(statsdf["avg"].values):
        ax3.text(
            v + 0.5,
            i,
            f"{v:.0f}",
            color=statsdf["color"].values[i],
            va="center",
        )

    # Create a manual legend
    ax3.legend(
        [
            ax3.bar(0, 0, color="r")[0],
            ax3.bar(0, 0, color="g")[0],
            ax3.bar(0, 0, color="b")[0],
        ],
        ["Federal ASOS", "Federal AWOS", "Non-Federal AWOS"],
        loc=(-2.5, 1.02),
        ncol=3,
    )

    # --------------------------------------
    ax4 = fig.add_axes((x0 + xwidth * 3 + 0.1, y0, xwidth, yheight))
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)

    ax4.barh(
        statsdf.index.values,
        statsdf["afternoon_rh90"].values,
        color=statsdf["color"].values,
    )
    ax4.set_xticks([5, 20, 40, 60])
    ax4.grid(axis="x")
    ax4.set_xlim(0, statsdf["afternoon_rh90"].max() + 3)
    ax4.set_xlabel("Noon-8PM RH > 90%\nFrequency [%]")
    ax4.set_yticks([])
    ax4.set_ylim(*ax.get_ylim())

    # Label the bars with integer value
    for i, v in enumerate(statsdf["afternoon_rh90"].values):
        ax4.text(
            v + 0.5,
            i,
            f"{v:.0f}",
            color=statsdf["color"].values[i],
            va="center",
        )

    # Create figure wide horizontal lines every 5 values to help with
    # Readability
    axpos = ax.get_position()
    axheight = axpos.y1 - axpos.y0
    for y in range(0, len(statsdf.index.values), 5):
        yloc = axpos.y0 + (y / len(statsdf.index.values)) * axheight
        fig.add_artist(
            Line2D(
                [0.05, 0.95],
                [yloc, yloc],
                color="k",
                alpha=0.3,
                linewidth=0.5,
                zorder=1,
            ),
        )

    fig.savefig("260730.png")


if __name__ == "__main__":
    main()
