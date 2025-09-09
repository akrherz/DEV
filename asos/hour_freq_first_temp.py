"""What was the hour of the first fall temp min"""

from datetime import timedelta

import pandas as pd
from pyiem.database import get_dbconn
from pyiem.plot import figure_axes


def main():
    """Go"""
    pgconn = get_dbconn("asos")
    df = pd.read_sql(
        "select extract(year from valid)::int as year, "
        "min(valid at time zone 'UTC') from alldata "
        "where station = 'DSM' and extract(month from valid) > 8 and "
        "tmpf < 32 GROUP by year ORDER by year",
        pgconn,
        index_col="year",
    )
    df["cst_hour"] = (
        df["min"] - timedelta(hours=5) + timedelta(minutes=10)
    ).dt.hour

    (fig, ax) = figure_axes()
    gdf = df.groupby("cst_hour").count()
    ax.bar(gdf.index.values, gdf["min"])
    ax.annotate(
        "19 Oct 2020\n11 AM",
        xy=(11, 1),
        xytext=(50, 50),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="0.8"),
        arrowprops=dict(
            arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=1"
        ),
    )
    ax.grid(True)
    ax.set_ylabel("Number of Years")
    ax.set_title(
        f"(DSM) Des Moines Airport ({df.index.min()}-{df.index.max()})\n"
        "Frequency of given hour having first fall season < 32°F temp."
    )
    ax.set_xticks(range(0, 24, 4))
    ax.set_xticklabels(["Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"])
    ax.set_xlabel("Central Daylight Time")
    fig.savefig("211022.png")


if __name__ == "__main__":
    main()
