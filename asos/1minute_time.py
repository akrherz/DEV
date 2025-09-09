"""Time close to the high."""

import calendar

import pandas as pd
import seaborn as sns
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("asos1min") as conn:
        df = pd.read_sql(
            """
            with highs as (
                SELECT date(valid) as date,
                max(tmpf) as high,
                min(tmpf) as low from alldata_1minute
                WHERE station = 'DSM' and tmpf is not null
                GROUP by date
            ),
            obs as (
                SELECT valid from alldata_1minute o, highs h WHERE
                o.station = 'DSM' and date(o.valid) = h.date and
                o.tmpf >= h.high - 3 and valid < '2022-01-01'
            )

            SELECT date(valid) as date, count(*) from obs GROUP by date
        """,
            conn,
            index_col=None,
        )
    df["date"] = pd.to_datetime(df["date"])
    df["doy"] = pd.to_numeric(df["date"].dt.strftime("%j"))
    df["month"] = df["date"].dt.month

    title = (
        "Time with Temperature within Three Degrees Fahrenheit of Daily High\n"
        "based on 1 minute data for Des Moines 2000-2021"
    )
    (fig, ax) = figure_axes(apctx={"_r": "43"}, title=title)
    sns.violinplot(x="month", y="count", data=df, ax=ax, inner="box", width=1)
    ax.set_ylim(0, 24 * 60 + 1)
    ax.set_yticks(range(0, 24 * 60 + 1, 120))
    ax.set_yticklabels(range(0, 25, 2))
    ax.grid(True)
    ax.set_ylabel("Hours")
    ax.set_xlabel("Month of Year")
    ax.axhline(12 * 60, lw=1.5, color="k")
    ax.set_xticks(range(0, 12))
    ax.set_xticklabels(calendar.month_abbr[1:])
    # ax.scatter(df['doy'].values, df['count'].values)
    fig.savefig("220207.png")


if __name__ == "__main__":
    main()
