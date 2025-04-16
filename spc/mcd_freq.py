"""
Note the mcd table now explicitly stores this.
"""

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure_axes


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        data = pd.read_sql(
            sql_helper("""
    select watch_confidence, count(*) from mcd
    where watch_confidence is not null GROUP by watch_confidence
    order by watch_confidence
                       """),
            conn,
        )
    data["freq"] = data["count"] / data["count"].sum() * 100.0
    (fig, ax) = figure_axes(
        title="Storm Prediction Center :: Mesoscale Discussion (MCD)",
        subtitle=(
            f"MCD's with Watch Confidence ({data['count'].sum():.0f}, "
            "1 May 2012 - 16 Apr 2025)"
        ),
        figsize=(8, 6),
    )

    ax.set_ylim(0, data["freq"].max() * 1.2)
    ax.bar(np.arange(6), data["freq"].to_numpy(), align="center")
    for i, row in data.iterrows():
        ax.text(
            i,
            row["freq"] + 1,
            f"{row['freq']:.1f}%",
            va="bottom",
            ha="center",
            bbox=dict(color="#EEEEEE"),
        )
    ax.set_xticks(range(6))
    ax.set_xticklabels([f"{v}%" for v in data["watch_confidence"].to_list()])
    ax.grid(True)
    ax.set_ylabel("Frequency (%)")
    ax.set_xlabel("Watch Confidence (%)")

    fig.text(
        0.01,
        0.01,
        "@akrherz, based on unofficial IEM archives, generated 16 Apr 2025",
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
