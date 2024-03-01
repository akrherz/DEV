"""Request for maps and data of products without SVS updates."""

import calendar

import seaborn as sns

from pandas.io.sql import read_sql
from pyiem.plot import get_cmap
from pyiem.plot.use_agg import plt
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_sql(
            """
        WITH data as (
            SELECT wfo, eventid, extract(year from issue)::int as year,
            extract(month from issue) as month, phenomena,
            max(case when svs is not null then 1 else 0 end) as hit from
            warnings where issue > '2008-01-01' and
            issue < '2021-01-01' and phenomena in ('SV', 'TO', 'FF')
            and significance = 'W'
            GROUP by wfo, eventid, year, month, phenomena
        )
        SELECT year, month, sum(hit) as got_update, count(*) as total_events
        from data GROUP by year, month ORDER by year, month ASC
        """,
            conn,
        )
    df["no_update_percent"] = (
        100.0 - df["got_update"] / df["total_events"] * 100.0
    )
    overall = 100.0 - df["got_update"].sum() / df["total_events"].sum() * 100.0
    df = df.pivot("year", "month", "no_update_percent")
    # sns.jointplot(
    #    df['total_events'], df['no_update_percent'], kind="hex",
    #    color="#4CB391")
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(
        df,
        annot=True,
        fmt=".1f",
        linewidths=0.5,
        ax=ax,
        cmap=get_cmap("terrain_r"),
    )
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_title(
        (
            "2008-2020 Percentage of NWS SVR+TOR+FFW Warnings by Year/Month\n"
            "without receiving a single SVS/FFS Update, "
            f"overall: {overall:.2f}%"
        )
    )
    ax.set_xlabel("Generated 24 Sep 2020 by @akrherz with unofficial data")
    for tick in ax.get_yticklabels():
        tick.set_rotation(0)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
