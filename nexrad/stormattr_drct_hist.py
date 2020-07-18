"""Histogram"""

from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Do great things"""
    pgconn = get_dbconn("postgis")
    alldf = read_sql(
        """
    select drct / 15 as bindrct, count(*) from nexrad_attributes_log
    where nexrad = 'DMX' and sknt >= 5 GROUP by bindrct ORDER by bindrct
    """,
        pgconn,
        index_col=None,
    )
    alldf["freq"] = alldf["count"] / alldf["count"].sum() * 100.0
    yestdf = read_sql(
        """
    select drct / 15 as bindrct, count(*) from nexrad_attributes_2017
    where nexrad = 'DMX' and valid > 'TODAY' and sknt >= 5
    GROUP by bindrct ORDER by bindrct
    """,
        pgconn,
        index_col=None,
    )
    yestdf["freq"] = yestdf["count"] / yestdf["count"].sum() * 100.0

    (fig, [ax1, ax2]) = plt.subplots(2, 1, sharex=True)
    ax1.bar(
        alldf["bindrct"] * 15.0 + 7.5,
        alldf["freq"],
        width=15,
        alpha=0.5,
        fc="r",
        label="2000-2017",
    )
    ax1.set_xticks(range(0, 361, 45))
    ax1.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax1.grid(True)
    ax1.legend()
    ax1.set_ylabel("Frequency [%]")
    ax1.set_title(
        (
            "Des Moines NEXRAD Storm Attribute Direction Frequency"
            "\n2000-2017 for storms traveling at least 5 knots speed"
        )
    )
    ax2.bar(
        yestdf["bindrct"] * 15.0 + 7.5,
        yestdf["freq"],
        width=15,
        alpha=0.5,
        fc="b",
        label="4 Jul 2017",
    )
    ax2.set_xticks(range(0, 361, 45))
    ax2.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax2.grid(True)
    ax2.set_ylim(top=ax1.get_ylim()[1])
    ax2.set_ylabel("Frequency [%]")
    ax2.legend()
    ax2.set_xlim(-1, 361)
    ax2.set_xlabel("Direction Storm Traveling From")
    fig.text(0.01, 0.01, "Plot Generated 4 Jul 2017")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
