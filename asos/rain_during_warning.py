"""
Compute the amount of precipitation that falls during a SVR,TOR warning
"""
import datetime

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot import figure_axes
from pyiem.util import get_dbconn, utc


def main():
    """GO Main Go."""
    obsdf = read_sql(
        "SELECT valid, precip, extract(year from valid)::int as year "
        "from alldata_1minute "
        "where station = %s and valid > %s and precip > 0 "
        "ORDER by valid ASC",
        get_dbconn("asos1min"),
        params=("DSM", utc(2002, 1, 1)),
        index_col="valid",
    )
    obsdf["inwarn"] = False
    obsdf["nearwarn"] = False

    warndf = read_sql(
        "SELECT issue, expire from sbw WHERE issue > '2002-01-01' and "
        "phenomena in ('TO', 'SV') and significance = 'W' and status = 'NEW' "
        "and ST_Contains(geom, "
        "GeomFromEWKT('SRID=4326;POINT(-93.66308 41.53397)')) "
        "ORDER by issue ASC",
        get_dbconn("postgis"),
        index_col=None,
    )
    td = datetime.timedelta(hours=1)
    for _, row in warndf.iterrows():
        obsdf.loc[row["issue"] : row["expire"], "inwarn"] = True
        obsdf.loc[row["issue"] - td : row["expire"] + td, "nearwarn"] = True

    # Yearly precips
    df = obsdf.groupby("year").sum().copy()

    # Warn only
    df["in"] = obsdf[obsdf["inwarn"]].groupby("year").sum()["precip"]
    # Near warn, but not in
    df["near"] = (
        obsdf[(obsdf["nearwarn"] & ~obsdf["inwarn"])]
        .groupby("year")
        .sum()["precip"]
    )
    df = df.fillna(0)
    df["out"] = df["precip"] - df["in"] - df["near"]
    print(df)

    title = (
        "Des Moines Yearly Airport Precipitation [2002-2021]\n"
        "Contribution during, near, and outside of TOR,SVR warning "
        "using one minute interval precipitation"
    )
    x = df.index.astype(int).tolist()

    fig, ax = figure_axes(title=title)
    width = 0.45
    height = 0.36
    ax.set_position([0.05, 0.54, width, height])
    ax.set_ylabel("Yearly Precip [inch]")
    ax.bar(x, df["in"], fc="r")
    ax.bar(x, df["near"], bottom=df["in"], fc="b")
    ax.bar(
        x,
        df["out"],
        bottom=(df["in"] + df["near"]),
        fc="g",
    )
    ax.set_xticks(range(2002, 2022, 4))
    ax.grid(True)

    ax = fig.add_axes([0.05, 0.08, width, height])
    ax.set_ylabel("Percentage [%]")
    ax.set_ylim(0, 100)

    df["in_per"] = df["in"] / df["precip"] * 100.0
    p = df["in"].sum() / df["precip"].sum() * 100.0
    ax.bar(x, df["in_per"], fc="r", label=f"During {p:.1f}%")

    df["near_per"] = df["near"] / df["precip"] * 100.0
    p = df["near"].sum() / df["precip"].sum() * 100.0
    ax.bar(
        x,
        df["near_per"],
        bottom=df["in_per"],
        fc="b",
        label=f"+/- 1 hour {p:.1f}%",
    )

    df["out_per"] = df["out"] / df["precip"] * 100.0
    p = df["out"].sum() / df["precip"].sum() * 100.0
    ax.bar(
        x,
        df["out_per"],
        bottom=(df["in_per"] + df["near_per"]),
        fc="g",
        label=f"Outside {p:.1f}%",
    )

    ax.legend(ncol=3, loc=(0.03, 1.03))
    ax.grid(True)
    ax.set_xticks(range(2002, 2022, 4))
    ax.set_xlabel("2021 thru 16 Sept, yearly precip may have missing data")

    ax = fig.add_axes([0.58, 0.4, 0.37, 0.37])
    idx = pd.MultiIndex.from_product([obsdf["precip"].unique(), [True, False]])
    gdf = (
        obsdf[["precip", "inwarn", "year"]]
        .groupby(["precip", "inwarn"])
        .count()
        .reindex(idx)
        .fillna(0)
        .transpose()
    )
    x = []
    y = []
    for val in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]:
        if (val, True) in gdf.columns:
            x.append(val)
            hit = gdf[(val, True)].iloc[0]
            miss = gdf[(val, False)].iloc[0]
            freq = hit / float(hit + miss) * 100.0
            y.append(freq)
            ax.text(
                val,
                freq + 5,
                f"{freq:.0f}%",
                ha="center",
                bbox=dict(color="white", boxstyle="square,pad=0"),
                va="bottom",
            )

    ax.bar(x, y, width=0.01)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Frequency [%]")
    ax.set_title(
        "Frequency that given minute precipitation total\n"
        "happened during warning"
    )
    ax.grid(True)

    fig.savefig("210917.png")


if __name__ == "__main__":
    main()
