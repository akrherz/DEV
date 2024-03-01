"""Yearly rank."""

import calendar

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes


def main():
    """Go Main."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            """
            with data as (
                select distinct date(issue), wfo, eventid from warnings
                where phenomena = 'TO' and significance = 'W'),
            agg as (select date, count(*) from data GROUP by date),
            agg2 as (select extract(year from date) as year, date, count,
                rank() OVER (PARTITION by extract(year from date)
                order by count desc)
                from agg)
            select * from agg2 where rank = 1 order by year asc
            """,
            conn,
            index_col="year",
            parse_dates="date",
        )
    df["doy"] = df["date"].dt.dayofyear

    fig, ax = figure_axes(
        title="Yearly Date of [Max Number] of NWS Tornado Warnings Issued",
        subtitle=(
            "Based on unofficial IEM archives computed for "
            "US Central Timezone Day"
        ),
        figsize=(8, 8),
    )

    ax.barh(df.index.values, df["doy"].values, ec="b", fc="b")
    # Label each bar with the date and count
    for year, row in df.iterrows():
        ax.text(
            row["doy"] + 10,
            year,
            f"{row['date']:%b %-d, %Y} [{row['count']}]",
            bbox={"color": "white", "pad": 0},
            va="center",
        )
    ax.set_ylim(1985.5, 2023.5)
    ax.set_xlim(0, 390)
    ax.set_xlabel("Day of Year, [count of daily maxes for month]")
    ax.set_ylabel("Year")
    ax.grid(True)
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    # Compute the monthly counts
    monthly = (
        df.groupby(df["date"].dt.month).count().reindex(range(1, 13)).fillna(0)
    )
    # use that value within the xtick labels
    xticklabels = []
    for month in range(1, 13):
        xticklabels.append(
            f"{calendar.month_abbr[month]}\n[{monthly.at[month, 'date']:.0f}]"
        )
    ax.set_xticklabels(xticklabels)
    fig.savefig("231121.png")


if __name__ == "__main__":
    main()
