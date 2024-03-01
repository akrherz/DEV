"""Plot the daily component of the yearly total."""

from calendar import month_abbr

import click
import numpy as np

import pandas as pd
from matplotlib.ticker import MaxNLocator
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure


@click.command()
@click.option("--huc12", help="HUC 12 ID")
def main(huc12):
    """."""
    with get_sqlalchemy_conn("idep") as conn:
        hucdf = pd.read_sql(
            "select name from huc12 where scenario = 0 and huc_12 = %s",
            conn,
            params=(huc12,),
        )
        df = pd.read_sql(
            """
            select valid, avg_delivery * 4.463 as delivery_ta from
            results_by_huc12 where scenario = 0 and huc_12 = %s
            and valid < '2024-01-01'
            order by delivery_ta DESC
            """,
            conn,
            params=(huc12,),
            index_col="valid",
            parse_dates="valid",
        )

    yearly = df.groupby(df.index.year).sum()
    df["yearly"] = df.index.year.map(yearly["delivery_ta"])
    df["daily_contrib"] = df["delivery_ta"] / df["yearly"] * 100.0
    df["daily_rank"] = df.groupby(df.index.year)["daily_contrib"].rank(
        method="first", ascending=False
    )
    fig = figure(
        title=f"HUC12 {huc12} {hucdf.at[0, 'name']}",
        subtitle=(
            "Contribution of Yearly Soil Loss [T/a] "
            "over Top 5 Most Erosive Days"
        ),
        logo="dep",
        figsize=(10.24, 7.68),
    )
    ax = fig.add_axes([0.1, 0.2, 0.5, 0.65])

    # create a stacked bar chart by year of the top 5 contributors
    bottom = np.zeros(2024 - 2007)
    for i in range(1, 6):
        df2 = df[df["daily_rank"] == i].sort_index()
        ax.bar(
            df2.index.year,
            df2["daily_contrib"],
            bottom=bottom,
            label=f"#{i}: {df2['daily_contrib'].mean():.1f}%",
        )
        bottom += df2["daily_contrib"].values
    # place labels on the top of the bars
    for year in range(df.index.year.min(), df.index.year.max() + 1):
        ax.text(
            year,
            105,
            f"{yearly.at[year, 'delivery_ta']:.1f}",
            ha="center",
            va="center",
            color="black",
            bbox=dict(facecolor="white", edgecolor="none", pad=1),
            rotation=45,
        )
    ax.text(
        0.02,
        1.05,
        "Anual Loss ->",
        transform=ax.transAxes,
        ha="right",
        va="center",
    )
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid()
    ax.legend(
        loc=(0.0, -0.2), ncol=5, title="Daily Rank and Overall Contribution"
    )
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylabel("Percentage of Yearly Soil Loss [%]")

    ax = fig.add_axes([0.61, 0.15, 0.35, 0.75], frame_on=False)
    ax.set_xticks([])
    ax.set_yticks([])
    data = []
    for i, month in enumerate(month_abbr[1:], 1):
        data.append(
            [
                month,
                df[df["daily_rank"] == 1].index.month.value_counts().get(i, 0),
                df[df["daily_rank"] == 2].index.month.value_counts().get(i, 0),
                df[df["daily_rank"] == 3].index.month.value_counts().get(i, 0),
                df[df["daily_rank"] == 4].index.month.value_counts().get(i, 0),
                df[df["daily_rank"] == 5].index.month.value_counts().get(i, 0),
            ]
        )

    ax.table(
        cellText=[["Month", "1", "2", "3", "4", "5"], *data],
        cellLoc="left",
        bbox=[0, 0.1, 1, 0.8],
        loc="center",
    )
    ax.text(0.5, 0.97, "Monthly Frequency of Top 5 Days", ha="center")
    ax.set_ylim(0, 1)

    fig.savefig(f"/tmp/{huc12}_daily_components.png")


if __name__ == "__main__":
    main()
