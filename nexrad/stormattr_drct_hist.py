"""Histogram"""

import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_sqlalchemy_conn


def main():
    """Do great things"""
    with get_sqlalchemy_conn("radar") as pgconn:
        alldf = pd.read_sql(
            """
        select drct / 15 as bindrct, count(*) from nexrad_attributes_log
        where nexrad = 'DMX' and sknt >= 5 and
        extract(month from valid) in (5, 6) GROUP by bindrct ORDER by bindrct
        """,
            pgconn,
            index_col=None,
        )
        yestdf = pd.read_sql(
            """
        select drct / 15 as bindrct, count(*) from nexrad_attributes_2023
        where nexrad = 'DMX' and valid > '2023-06-01' and sknt >= 5
        GROUP by bindrct ORDER by bindrct
        """,
            pgconn,
            index_col=None,
        )
    alldf["freq"] = alldf["count"] / alldf["count"].sum() * 100.0
    yestdf["freq"] = yestdf["count"] / yestdf["count"].sum() * 100.0

    fig = figure(
        title=(
            "Des Moines NEXRAD Storm Attribute Direction Frequency [May-June]"
        ),
        subtitle="2000-2023 for storms traveling at least 5 knots speed",
        figsize=(10.24, 7.68),
    )
    ax1 = fig.add_axes([0.1, 0.55, 0.8, 0.35])
    ax2 = fig.add_axes([0.1, 0.1, 0.8, 0.35])
    ax1.bar(
        alldf["bindrct"] * 15.0 + 7.5,
        alldf["freq"],
        width=15,
        alpha=0.5,
        fc="r",
        label="2000-2023",
    )
    ax1.set_xticks(range(0, 361, 45))
    ax1.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax1.grid(True)
    ax1.legend()
    ax1.set_ylabel("Frequency [%]")
    ax1.set_xlim(-1, 361)
    ax2.bar(
        yestdf["bindrct"] * 15.0 + 7.5,
        yestdf["freq"],
        width=15,
        alpha=0.5,
        fc="b",
        label="1-6 Jun 2023",
    )
    ax2.set_xticks(range(0, 361, 45))
    ax2.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax2.grid(True)
    ax2.set_ylim(top=ax1.get_ylim()[1])
    ax2.set_ylabel("Frequency [%]")
    ax2.legend()
    ax2.set_xlim(-1, 361)
    ax2.set_xlabel("Direction Storm Traveling From")
    fig.savefig("230607.png")


if __name__ == "__main__":
    main()
