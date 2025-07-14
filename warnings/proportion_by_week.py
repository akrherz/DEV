"""Proportional counts by week for certain warning types."""

import calendar
import os

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.vtec import NWS_COLORS, get_ps_string
from pyiem.plot import figure


def get_data():
    with get_sqlalchemy_conn("postgis") as pgconn:
        weekly = pd.read_sql(
            """
            select extract(week from issue) as week,
            phenomena, count(*) as total,
            sum(case when wfo in ('DMX', 'FSD', 'OAX', 'DVN', 'ARX')
             then 1 else 0 end) as count_iowa
            from sbw where phenomena in ('TO', 'SV', 'FF')
            and status = 'NEW' and significance = 'W' and issue > '2001-01-01'
            group by week, phenomena order by week, phenomena
        """,
            pgconn,
        )
    # Drop week 53 as it is not a full week
    weekly = weekly[weekly["week"] != 53]
    weekly.to_csv("weekly.csv", index=False)


def main():
    """."""
    if not os.path.isfile("weekly.csv"):
        get_data()
    weekly = pd.read_csv("weekly.csv")

    iowa_total = weekly.groupby("week")["count_iowa"].sum()
    all_total = weekly.groupby("week")["total"].sum()

    fig = figure(
        title="Weekly Normalized NWS Warning Counts (2001-2025)",
        subtitle=(
            "Bars are the relative percentage of the three warning total"
            ", till 13 July 2025"
        ),
        figsize=(8, 6),
    )
    ax2 = fig.add_axes((0.1, 0.05, 0.85, 0.38))
    ax = fig.add_axes((0.1, 0.52, 0.85, 0.38))
    ax.set_ylabel("Iowa WFOs\n(DMX, FSD, OAX, DVN, ARX)")
    bottom = 0
    for ph in ["TO", "SV", "FF"]:
        df = weekly[weekly["phenomena"] == ph][
            ["week", "count_iowa"]
        ].set_index("week")
        proportion = df["count_iowa"] / iowa_total * 100.0
        ax.bar(
            proportion.index,
            proportion.values,
            bottom=bottom,
            label=get_ps_string(ph, "W"),
            width=0.8,
            align="center",
            color=NWS_COLORS[f"{ph}.W"],
        )
        bottom += proportion.values

    ax.set_ylim(0, 100)
    ax.set_xlim(0.5, 52.5)
    ax.legend(
        loc=(0.05, -0.25),
        ncol=3,
        fontsize=10,
    )
    # Approximate monthly tick labels
    ax.set_xticks(
        [1, 5.3, 9.6, 14, 18.3, 22.6, 27, 31.3, 35.6, 40, 44.3, 48.6]
    )
    ax.set_xticklabels(calendar.month_abbr[1:])

    ax2.set_ylabel("United States (All WFOs)")

    bottom = 0
    for ph in ["TO", "SV", "FF"]:
        df = weekly[weekly["phenomena"] == ph][["week", "total"]].set_index(
            "week"
        )
        proportion = df["total"] / all_total * 100.0
        ax2.bar(
            proportion.index,
            proportion.values,
            bottom=bottom,
            label=ph,
            width=0.8,
            align="center",
            color=NWS_COLORS[f"{ph}.W"],
        )
        bottom += proportion.values

    ax2.set_xlim(0.5, 52.5)
    ax2.set_yticks(range(0, 101, 10))
    ax2.set_ylim(0, 100)
    ax2.set_xticks(
        [1, 5.3, 9.6, 14, 18.3, 22.6, 27, 31.3, 35.6, 40, 44.3, 48.6]
    )
    ax2.set_xticklabels(calendar.month_abbr[1:])

    fig.savefig("250714.png")


if __name__ == "__main__":
    main()
