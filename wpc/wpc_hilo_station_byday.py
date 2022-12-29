"""Visualize when a station is the max/min."""
from calendar import month_abbr

import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
            select name, state, date from wpc_national_high_low WHERE
            n_x = 'N'
            """,
            conn,
            index_col=None,
            parse_dates=["date"],
        )
    gdf = (
        df.groupby(["name", "state"])
        .count()
        .sort_values("date", ascending=False)
        .rename(columns={"date": "count"})
        .reset_index()
    )
    fig, ax = figure_axes(
        title="Jul 2008-2022 WPC Top 10 Locations for Daily Min Temperature",
        subtitle="Dots indicate days of the year with min",
    )
    ax.set_position([0.2, 0.1, 0.75, 0.8])
    ylabels = [""] * 10
    for i, row in gdf.head(10).iterrows():
        df2 = df[(df["name"] == row["name"]) & (df["state"] == row["state"])]
        ax.scatter(df2["date"].dt.day_of_year, [9 - i] * len(df2.index))
        ylabels[9 - i] = f"{row['name']}, {row['state']} [{row['count']}]"
    ax.set_yticks(range(0, 10))
    ax.set_yticklabels(ylabels)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(month_abbr[1:])
    ax.set_xlim(0, 366)
    ax.grid(True)

    fig.savefig("wpc_min.png")


if __name__ == "__main__":
    main()
