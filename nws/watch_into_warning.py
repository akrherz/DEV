"""Some stats based on distance from issuance time to issue."""

import os

import matplotlib.pyplot as plt
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from tqdm import tqdm


def workflow(pgconn, wfo: str, phenomena: str):
    """do work"""
    df = pd.read_sql(
        sql_helper("""
    WITH mywatches as (
        SELECT product_issue, eventid, wfo, ugc, issue,
        greatest(expire, init_expire) as expire
        from warnings w
        WHERE phenomena = :phenomena and significance = 'A' and wfo = :wfo
        and issue > '2006-01-01'),
    mywarnings as (
        SELECT wfo, ugc, issue, expire from warnings w
        WHERE phenomena = :phenomena and significance = 'W' and wfo = :wfo
        and issue > '2006-01-01'),
    agg1 as (
        SELECT a.wfo, a.eventid, a.ugc as watch_ugc, w.ugc as warn_ugc,
        a.product_issue, a.issue as watch_issue, a.expire as watch_expire,
        w.issue as warning_issue from mywatches a LEFT JOIN mywarnings w on
        (a.ugc = w.ugc
         and a.issue <= w.issue and a.expire > w.issue)),
    agg2 as (
        select wfo, extract(year from watch_issue) as yr,
        eventid, watch_ugc, warn_ugc,
        product_issue, watch_issue, watch_expire,
        min(warning_issue) as warning_issue from agg1
        GROUP by wfo, yr, eventid, watch_ugc, warn_ugc,
        product_issue, watch_issue, watch_expire
    )

    select wfo, yr::int, eventid,
    min(product_issue at time zone 'UTC') as product_issue,
    min(watch_issue at time zone 'UTC') as watch_issue,
    extract('epoch' from min(watch_issue) -
                         min(product_issue)) / 60. as minutes,
    count(*) as watch_zones,
    sum(case when warning_issue is not null then 1 else 0 end) as warn_counties
    from agg2 GROUP by wfo, yr, eventid ORDER by yr ASC, eventid ASC
    """),
        pgconn,
        params={"wfo": wfo, "phenomena": phenomena},
        index_col=None,
    )
    if df.empty:
        return None, None, None
    eff = len(df[df["warn_counties"] > 0].index) / float(len(df.index)) * 100.0
    overall = (
        df["warn_counties"].sum() / float(df["watch_zones"].sum()) * 100.0
    )
    print(f"WFO: {wfo} Efficiency: {eff:.1f}  Overall: {overall:.1f}")
    return df["warn_counties"].sum(), df["watch_zones"].sum(), overall


def main():
    """Go Main"""
    nt = NetworkTable("WFO")
    rows = []
    with get_sqlalchemy_conn("postgis") as pgconn:
        for wfo in tqdm(nt.sts.keys()):
            warn, watch, overall = workflow(pgconn, wfo, "HW")
            rows.append(
                {"wfo": wfo, "warn": warn, "watch": watch, "overall": overall}
            )
    df = pd.DataFrame(rows)
    df.to_csv("wfo.csv")


def plot():
    """Make a pretty plot"""
    if not os.path.isfile("wfo.csv"):
        main()
    df = pd.read_csv("wfo.csv")
    df = df.set_index("wfo")
    overall = df["warn"].sum() / df["watch"].sum() * 100.0
    mp = MapPlot(
        sector="conus",
        title=(
            "Percentage of Counties/Parishes in a High Wind Watch "
            "receiving a High Wind Warning"
        ),
        subtitle=(
            f"2006-2025, Overall: {df['warn'].sum():,.0f} / "
            f"{df['watch'].sum():,.0f} = {overall:.1f}%"
        ),
    )
    cmap = plt.get_cmap("plasma")
    df2 = df[df["overall"].notnull()]
    mp.fill_cwas(
        df2["overall"].to_dict(),
        cmap=cmap,
        bins=range(0, 101, 10),
        extend="max",
        units="%",
        lblformat="%.0f",
        ilabel=True,
    )
    mp.postprocess(filename="test.png")
    mp.close()


if __name__ == "__main__":
    plot()
