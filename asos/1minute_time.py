"""Time close to the high."""
import calendar

from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt
import seaborn as sns
import pandas as pd
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    pgconn = get_dbconn("asos")
    df = read_sql(
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
            o.tmpf >= ((h.high + h.low) / 2.) and valid < '2020-01-01'
        )

        SELECT date(valid) as date, count(*) from obs GROUP by date
    """,
        pgconn,
        index_col=None,
    )
    df["date"] = pd.to_datetime(df["date"])
    df["doy"] = pd.to_numeric(df["date"].dt.strftime("%j"))
    df["month"] = df["date"].dt.month

    (fig, ax) = plt.subplots(1, 1)
    sns.violinplot(x="month", y="count", data=df, ax=ax, inner="box")
    ax.set_ylim(0, 24 * 60 + 1)
    ax.set_yticks(range(0, 24 * 60 + 1, 120))
    ax.set_yticklabels(range(0, 24, 2))
    ax.grid(True)
    ax.set_ylabel("Hours")
    ax.set_xlabel("Month of Year")
    ax.axhline(12 * 60, lw=1.5, color="k")
    ax.set_title(
        "Time with Temperature above Daily Average (high+low)/2\nbased on 1 minute data for Des Moines 2000-2010"
    )
    ax.set_xticks(range(0, 12))
    ax.set_xticklabels(calendar.month_abbr[1:])
    # ax.scatter(df['doy'].values, df['count'].values)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
