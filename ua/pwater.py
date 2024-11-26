"""
Look at preciptable water
"""

import numpy as np
import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import get_sqlalchemy_conn


def run():
    """Run()."""
    # get 500 heights
    with get_sqlalchemy_conn("raob") as conn:
        pwater = pd.read_sql(
            """
        select date(valid at time zone 'UTC') as date, pwater_mm
        from raob_flights f
        where f.station in ('KOAX', 'KOVN', 'KOMA') and
        extract(hour from valid at time zone 'UTC') = 0 and
        extract(month from valid) = 5
        ORDER by date ASC
        """,
            conn,
            parse_dates="date",
            index_col="date",
        )
    # Get obs
    with get_sqlalchemy_conn("iem") as conn:
        obs = pd.read_sql(
            """
            select
            date(valid + '5 hours'::interval), sum(phour) from
            hourly h JOIN stations t on (h.iemid = t.iemid) WHERE
            t.id = 'OMA' and t.network = 'NE_ASOS' and phour > 0
            and extract(month from valid) = 5 and
            (extract(hour from valid) >= 19 or extract(hour from valid) < 7)
            GROUP by date ORDER by date ASC
            """,
            conn,
            parse_dates="date",
            index_col="date",
        )
    (
        obs.reindex(pd.date_range(obs.index.values[0], obs.index.values[-1]))
        .fillna(0)
        .assign(pwater=pwater["pwater_mm"])
        .to_csv("pwater.csv")
    )


def main():
    """Go Main Go."""
    df = pd.read_csv("pwater.csv", parse_dates=["date"])
    df = df[df["pwater"].notna()]
    df["pwater"] = df["pwater"] / 25.4

    (fig, ax) = figure_axes(
        title=(
            "Omaha 7 PM Precipitable Water + Next 12 Hour Rainfall during May"
        ),
        subtitle=(f"{df['date'].min():%Y/%m/%d} to " "2023-05-23"),
        figsize=(8.0, 6.0),
    )
    ax.scatter(df["pwater"].values, df["sum"].values)
    d2023 = df[df["date"] > pd.Timestamp("2023/01/01")]
    ax.scatter(
        d2023["pwater"].values, d2023["sum"].values, color="r", label="2023"
    )
    quantiles = df["pwater"].quantile(np.arange(0.0, 1.01, 0.2)).values
    x = []
    y = []
    for bot, top in zip(quantiles[:-1], quantiles[1:], strict=False):
        x.append(top)
        sample = df[(df["pwater"] >= bot) & (df["pwater"] < top)]
        y.append((sample["sum"] > 0.0).sum() / len(sample.index) * 100.0)
    ax2 = ax.twinx()
    ax2.plot(x, y, label="Mean Estimate", color="g")
    ax2.set_ylim(0, 60)
    ax2.set_ylabel("Percent Days with Precip", color="g")
    ax.set_ylim(-0.02, 6)
    ax.legend()
    ax.grid(True)
    ax.set_ylabel("Precipitation [inch]")
    ax.set_xlabel("Sounding Precipitable Water [inch]")

    fig.savefig("230525.png")


if __name__ == "__main__":
    main()
