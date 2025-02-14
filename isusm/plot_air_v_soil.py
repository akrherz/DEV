"""Try something fancy."""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure
from pyiem.util import c2f


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            sql_helper("""
            SELECT valid, tair_c_avg_qc as air, sv_t2_qc as soil
            from sm_minute where station = 'AKCI4'
            and tair_c_avg_qc is not null and sv_t2_qc is not null
            and valid > '2025-01-18' ORDER by valid ASC
        """),
            conn,
            index_col=None,
        )
    df["air"] = c2f(df["air"])
    df["soil"] = c2f(df["soil"])

    fig = figure(
        title="ISU Soil Moisture -- Ames Kitch Farm Temperature Comparison",
        subtitle=(
            "Air Temp vs Soil Temp at 2 inches, "
            "★ is start of period, ● is end of period"
        ),
        figsize=(8, 6),
    )
    c1 = [0.12156863, 0.46666667, 0.70588235, 1.0]
    c2 = [1.0, 0.49803922, 0.05490196, 1.0]
    ax = fig.add_axes((0.1, 0.1, 0.7, 0.8))
    ax1 = fig.add_axes((0.72, 0.6, 0.25, 0.15), xticks=[], yticks=[])
    # Place title on the left side with a pretty and rounded box
    ax1.set_title(
        "Air Temp Time Series", loc="left", bbox=dict(facecolor="tan")
    )
    ax2 = fig.add_axes((0.72, 0.3, 0.25, 0.15), xticks=[], yticks=[])
    ax2.set_title(
        "Soil Temp Time Series", loc="left", bbox=dict(facecolor="tan")
    )

    df2 = df[
        (df["valid"] > "2025-01-19") & (df["valid"] < "2025-01-21")
    ].copy()
    df2["x"] = df2["valid"] - df2["valid"].iloc[0]
    ax1.plot(df2["x"], df2["air"], color=c1)
    ax2.plot(df2["x"], df2["soil"], color=c1)
    ax.scatter(df2["soil"], df2["air"], label="19-20 Jan 2025, No Snow")
    # Plot the first point in the same color, but with a star marker
    ax.scatter(
        df2["soil"].iloc[0],
        df2["air"].iloc[0],
        color="k",
        marker="*",
        s=150,
    )
    ax.scatter(
        df2["soil"].iloc[-1],
        df2["air"].iloc[-1],
        color="k",
        marker="o",
        s=150,
    )

    df2 = df[df["valid"] > "2025-02-12"].copy()
    ax.scatter(
        df2["soil"], df2["air"], label="12-13 Feb 2025, ~4 inches of Snow"
    )
    df2["x"] = df2["valid"] - df2["valid"].iloc[0]
    ax1.plot(df2["x"], df2["air"], color=c2)
    ax2.plot(df2["x"], df2["soil"], color=c2)
    ax.scatter(
        df2["soil"].iloc[0],
        df2["air"].iloc[0],
        color="k",
        marker="*",
        s=150,
    )
    ax.scatter(
        df2["soil"].iloc[-1],
        df2["air"].iloc[-1],
        color="k",
        marker="o",
        s=150,
    )

    ax.axhline(32, lw=2, color="r", zorder=2)
    ax.axvline(32, lw=2, color="r", zorder=2)

    ax.legend()
    ax.grid(True)
    ax.set_xlabel("2 inch Soil Temperature $^\circ$F", fontsize=14)
    ax.set_ylabel("~5 foot Air Temperature $^\circ$F", fontsize=14)
    fig.savefig("250214.png")


if __name__ == "__main__":
    main()
