"""Feature analysis."""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure_axes


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

    (fig, ax) = figure_axes(
        title="IEM Daily Feature Favorable Voting Percentage",
        figsize=(8, 6),
    )

    y = df["favorable"].rolling(60).mean()
    ax.plot(df.index.values, y, color="b", label="Trailing 60 day average")
    ax.legend(loc=4)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.set_ylabel("Good Votes (Percent of Total)")
    ax.set_xlim(df.index.values[0], df.index.values[-1])
    ax.set_xlabel(
        (
            "Total Votes; Good: %s (%.1f%%) "
            "Bad: %s (%.1f%%) Abstain: %s (%.1f%%)"
        )
        % (
            df["good"].sum(),
            df["good"].sum() / df["total"].sum() * 100.0,
            df["bad"].sum(),
            df["bad"].sum() / df["total"].sum() * 100.0,
            df["abstain"].sum(),
            df["abstain"].sum() / df["total"].sum() * 100.0,
        )
    )

    fig.savefig("230616.png")


if __name__ == "__main__":
    main()
