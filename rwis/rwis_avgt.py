"""Ancient."""

import calendar

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes


def main():
    """Go Main."""
    with get_sqlalchemy_conn("rwis") as conn:
        df = pd.read_sql(
            """
        select extract(doy from valid) as d, avg(tfs1), stddev(tfs1),
        sum(case when tfs1 < 32 then 1 else 0 end) as hits, count(*)
        from alldata
        where station = 'RAMI4' and extract(hour from valid) = 12
        and tfs1 between -30 and 160
        GROUP by d ORDER by d ASC
        """,
            conn,
            index_col="d",
        )
    df = (
        df.assign(freq=lambda df_: df_["hits"] / df_["count"] * 100.0)
        .rolling(14, min_periods=1, center=True)
        .mean()
    )

    (fig, ax) = figure_axes(
        title="2000-2022 Ames RWIS I-35 :: Average Noon Pavement Temperature",
        apctx={"_r": "43"},
    )

    ax.fill_between(
        df.index,
        df["avg"] - df["stddev"],
        df["avg"] + df["stddev"],
        color="tan",
        label="+/- 1 STD",
    )
    ax.plot(df.index, df["avg"], label="Average")
    # ax2 = ax.twinx()
    # ax2.plot(df.index, df["freq"], color="r", label="Frequency")
    # ax2.set_ylabel("Frequency of Freezing Temperature [%]", color="r")
    # ax2.set_ylim(0, 100)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlabel("Noon Central Daylight/Standard, 14 Day Smooth Applied")
    ax.set_xlim(1, 366)
    ax.plot([1, 366], [32, 32], linestyle="--")
    # ax.plot(doy, stddev, label='Pavement')
    ax.grid(True)
    ax.legend()
    ax.set_ylabel("Average Temperature °F", color="b")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
