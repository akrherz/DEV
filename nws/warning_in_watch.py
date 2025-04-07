"""Looking for frequency of warnings that had a watch."""

import os

import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from sqlalchemy.engine import Connection


@with_sqlalchemy_conn("postgis")
def get_data(conn: Connection = None):
    """Do the query!"""
    statsdf = pd.read_sql(
        sql_helper("""
    with warns as (
        select wfo, ugc, issue, expire from warnings
        where phenomena = 'HW' and significance ='W' and
        issue > '2005-10-01' and wfo = 'BOU'),
    watch as (
        select wfo, ugc, phenomena, issue,
        greatest(init_expire, expire) as expire
        from warnings where
        phenomena in ('HW') and significance = 'A' and wfo = 'BOU'),
    agg as (
        SELECT w.ugc, w.wfo, w.issue as w_issue, w.expire, a.ugc as a_ugc,
        a.phenomena,
        a.issue, a.expire from warns w LEFT JOIN watch a on (w.ugc = a.ugc
        and w.issue < a.expire and w.expire > a.issue))

    SELECT ugc, count(*), sum(case when phenomena = 'HW' then 1 else 0 end)
    as haswatch,
    sum(case when phenomena is null then 1 else 0 end) as nowatch from agg
    GROUP by ugc ORDER by ugc
                   """),
        conn,
        index_col="ugc",
    )
    return statsdf


def main():
    """Go Main."""
    cachedfn = "ugc.csv"
    if not os.path.isfile(cachedfn):
        statsdf = get_data()
        statsdf.to_csv(cachedfn)
    else:
        statsdf = pd.read_csv(cachedfn, index_col="ugc")

    statsdf["freq"] = statsdf["haswatch"] / statsdf["count"] * 100.0
    print(statsdf["freq"].to_dict())
    overall = statsdf["haswatch"].sum() / statsdf["count"].sum() * 100.0
    mp = MapPlot(
        sector="cwa",
        cwa="BOU",
        title=(
            "Percentage of Counties/Zones in High Wind Warning with a HW Watch"
        ),
        subtitle=(
            "Oct 2005 - 2 Apr 2025, Overall: "
            f"{statsdf['haswatch'].sum():,.0f} / "
            f"{statsdf['count'].sum():,.0f} = {overall:.1f}%"
        ),
    )
    cmap = get_cmap("plasma")
    mp.fill_ugcs(
        statsdf["freq"].to_dict(),
        cmap=cmap,
        bins=range(0, 101, 10),
        extend="neither",
        units="%",
        lblformat="%.0f",
        ilabel=True,
    )

    mp.fig.savefig("BOU_HWW_in_watch.png")


if __name__ == "__main__":
    main()
