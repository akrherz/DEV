"""Request for maps and data of products without SVS updates."""
import calendar

from pandas.io.sql import read_sql
import seaborn as sns
from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt


def main():
    """Go Main Go."""
    dbconn = get_dbconn("postgis")
    df = read_sql(
        """
    WITH data as (
        SELECT wfo, eventid, extract(year from issue)::int as year,
        extract(month from issue) as month, phenomena,
        max(case when svs is not null then 1 else 0 end) as hit from
        warnings where issue > '2008-01-01' and
        issue < '2019-01-01' and phenomena in ('SV', 'TO', 'FF')
        and significance = 'W' GROUP by wfo, eventid, year, month, phenomena
    )
    SELECT year, month, sum(hit) as got_update, count(*) as total_events
    from data GROUP by year, month ORDER by year, month ASC
    """,
        dbconn,
    )
    df["no_update_percent"] = (
        100.0 - df["got_update"] / df["total_events"] * 100.0
    )
    df = df.pivot("year", "month", "no_update_percent")
    # sns.jointplot(
    #    df['total_events'], df['no_update_percent'], kind="hex",
    #    color="#4CB391")
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(df, annot=True, fmt=".1f", linewidths=0.5, ax=ax)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_title(
        (
            "2008-2018 Percentage of SVR+TOR+FFW Warnings by Year/Month\n"
            "without receiving a single SVS/FFS Update"
        )
    )
    ax.set_xlabel("Generated 22 Feb 2019 by @akrherz with unofficial data")
    for tick in ax.get_yticklabels():
        tick.set_rotation(0)
    plt.gcf().savefig("test.png")


if __name__ == "__main__":
    main()
