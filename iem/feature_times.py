"""Feature analysis."""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure


def main():
    """GO Main Go."""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            sql_helper("""
            SELECT valid, good, bad, abstain,
            extract(hour from valid) as hour,
            extract(minute from valid) as minute from feature
            where good > 0 ORDER by valid
        """),
            conn,
            index_col="valid",
        )
    df["minutes"] = df["hour"] * 60 + df["minute"]
    df["total"] = df["good"] + df["bad"] + df["abstain"]
    df["favorable"] = df["good"] / df["total"] * 100.0

    fig = figure(
        title="IEM Daily Feature",
        subtitle="Voting percentages by year, voting option added in 2004",
        figsize=(8, 6),
    )
    ax = fig.add_axes((0.1, 0.15, 0.85, 0.7))

    gdf = df.groupby(df.index.year).sum().copy()
    gdf["good_pct"] = gdf["good"] / gdf["total"] * 100.0
    gdf["bad_pct"] = gdf["bad"] / gdf["total"] * 100.0
    gdf["abstain_pct"] = gdf["abstain"] / gdf["total"] * 100.0

    # Create stacked bar plot
    gdf[["good_pct", "bad_pct", "abstain_pct"]].plot(
        kind="bar",
        stacked=True,
        ax=ax,
        color=["green", "red", "blue"],
    )

    ax.legend(["Good", "Bad", "Abstain"], loc=(0.2, 1.01), ncol=3)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.set_ylabel("Percentage of Votes")
    gg = df["good"].sum() / df["total"].sum() * 100.0
    bb = df["bad"].sum() / df["total"].sum() * 100.0
    aa = df["abstain"].sum() / df["total"].sum() * 100.0
    ax.set_xlabel(
        f"Total Votes: Good {df['good'].sum():,.0f} ({gg:.1f}%), "
        f"Bad {df['bad'].sum():,.0f} ({bb:.1f}%), "
        f"Abstain {df['abstain'].sum():,.0f} ({aa:.1f}%)"
    )

    fig.savefig("250516.png")


if __name__ == "__main__":
    main()
