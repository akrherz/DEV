"""Days Suitable for Fieldwork."""

import calendar
import itertools

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes


def flip(items, ncol):
    return itertools.chain(*[items[i::ncol] for i in range(ncol)])


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("coop") as engine:
        df = pd.read_sql(
            """
            SELECT * from nass_iowa where metric = 'days suitable'
            order by valid asc
        """,
            engine,
            index_col="valid",
            parse_dates=["valid"],
        ).drop(columns=["load_time", "metric"])
    # reindex to fill out all the days
    df = df.reindex(pd.date_range(df.index[0], df.index[-1]))
    # backfill up to 6 days in a row with the previous value
    df = df.bfill(limit=6)

    # create 9 colors with blues for top 3 districts, reds for bottom 3
    # and greens for the middle 3
    colors = [
        "blue",
        "lightblue",
        "darkblue",
        "red",
        "pink",
        "darkred",
        "green",
        "lightgreen",
        "darkgreen",
        "black",
    ]

    fig, ax = figure_axes(
        title="USDA NASS: Frequency Day of Year is Suitable for Fieldwork",
        subtitle=(
            "1974-2023 weekly data, evenly weighted to daily, "
            "9 Iowa Crop Districts + Statewide"
        ),
        figsize=(8, 6),
    )
    for i, col in enumerate(df.columns):
        means = df[col].groupby(df.index.dayofyear).mean() / 7.0 * 100.0
        counts = df[col].groupby(df.index.dayofyear).count()
        # Require 10 years of data
        means = means[counts > 10]
        ax.plot(
            means.index.values,
            means,
            lw=3 if col == "iowa" else 1,
            color=colors[i],
            label=f"{col.upper()}: {means.mean():.1f}%",
        )

    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax.set_xticklabels([f"{FF} 1" for FF in calendar.month_abbr[1:]])
    ax.grid(True)
    ax.set_ylim(20, 85)
    ax.set_xlim(85, 340)
    ax.set_ylabel("Frequency Suitable for Fieldwork [%]")
    ax.set_yticks(range(20, 86, 5))

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(flip(handles, 3), flip(labels, 3), loc=4, ncol=3)

    fig.savefig("231222.png")


if __name__ == "__main__":
    main()
