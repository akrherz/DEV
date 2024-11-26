"""Produce a heatmap of OFE groupids."""

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes
from sqlalchemy import text


@click.command()
def main():
    """Go Main Go."""

    with get_sqlalchemy_conn("idep") as conn:
        ofedf = pd.read_sql(
            text("""
    select ofe, left(groupid, 1)::int as slpclass, count(*)
    from flowpath_ofes o
    JOIN flowpaths f on (o.flowpath = f.fid)
    WHERE f.scenario = 0 and groupid is not null GROUP by ofe, slpclass
    """),
            conn,
        )

    (fig, ax) = figure_axes(
        title="Percentage of OFE Ranks by Slope Class",
        subtitle="Daily Erosion Project",
        logo="dep",
    )
    xoff = -0.3
    for oferank in range(1, 6):
        df2 = ofedf[ofedf["ofe"] == oferank].copy()
        df2["percent"] = df2["count"] / df2["count"].sum() * 100.0
        ax.bar(
            df2["slpclass"] + xoff,
            df2["percent"],
            width=0.15,
            label=f"OFE Rank: {oferank}",
        )
        xoff += 0.15

    ax.set_xlabel("Slope Class")
    ax.set_ylabel("Percentage of OFE Ranks")
    ax.legend()
    ax.grid(True)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
