"""heatmap"""
import calendar

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
import seaborn as sns
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("asos")
    dfin = read_sql(
        """
    with mob as (
        select date_trunc('hour', valid) as ts, avg(dwpf) from alldata
        where station = 'MOB' and dwpf is not null GROUP by ts),
    cmi as (
        select date_trunc('hour', valid) as ts, avg(dwpf) from alldata
        where station = 'CMI' and dwpf is not null GROUP by ts),
    agg as (
        select m.ts, m.avg as dwpf, c.avg as tmpf
        from mob m JOIN cmi c on (m.ts = c.ts))
    select extract(month from ts) as month, extract(hour from ts) as hour,
    sum(case when dwpf >= tmpf then 1 else 0 end) / count(*)::float * 100.
    as freq from agg GROUP by month, hour ORDER by month, hour
    """,
        pgconn,
        index_col=None,
    )

    df = dfin.pivot("month", "hour", "freq")

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_title(
        (
            "Hourly Frequency of Mobile (MOB) Dew Point\n"
            "greater than or equal to Champaign (CMI) Dew Point"
        )
    )
    sns.heatmap(
        df, annot=True, fmt=".0f", linewidths=0.5, ax=ax, vmin=5, vmax=100
    )
    print(ax.get_yticks())
    ax.set_xlabel("Hour of Day (CDT or CST)")
    ax.set_xticklabels(
        [
            "Mid",
            "1AM",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "Noon",
            "1PM",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
        ]
    )
    ax.set_yticklabels(calendar.month_abbr[1:])
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
