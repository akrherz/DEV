"""Some stats based on distance from issuance time to issue."""

import sys

from tqdm import tqdm

import matplotlib.pyplot as plt
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def workflow(wfo, phenomena):
    """do work"""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        """
    WITH mywatches as (
        SELECT product_issue, eventid, wfo, ugc, issue,
        greatest(expire, init_expire) as expire
        from warnings w
        WHERE phenomena = %s and significance = 'A' and wfo = %s
        and issue > '2006-01-01'),
    mywarnings as (
        SELECT wfo, ugc, issue, expire from warnings w
        WHERE phenomena = %s and significance = 'W' and wfo = %s
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
    """,
        pgconn,
        params=(phenomena, wfo, phenomena, wfo),
        index_col=None,
    )
    if len(df.index) == 0:
        return None
    eff = len(df[df["warn_counties"] > 0].index) / float(len(df.index)) * 100.0
    overall = (
        df["warn_counties"].sum() / float(df["watch_zones"].sum()) * 100.0
    )
    print("WFO: %s Efficiency: %.1f  Overall: %.1f" % (wfo, eff, overall))
    return eff


def main():
    """Go Main"""
    nt = NetworkTable("WFO")
    rows = []
    for wfo in tqdm(nt.sts.keys()):
        rows.append(dict(wfo=wfo, freq=workflow(wfo)))
    df = pd.DataFrame(rows)
    df.to_csv("wfo.csv")


def plot():
    """Make a pretty plot"""
    df = pd.read_csv("wfo.csv")
    df = df.set_index("wfo")
    m = MapPlot(
        sector="conus",
        title="Percentage of Flash Flood Watches receiving 1+ FFW",
        subtitle="PRELIMINARY PLOT! Please do not share :)",
    )
    cmap = plt.get_cmap("jet")
    df2 = df[df["freq"].notnull()]
    m.fill_cwas(
        df2["freq"].to_dict(),
        cmap=cmap,
        units="%",
        lblformat="%.0f",
        ilabel=True,
    )
    m.postprocess(filename="test.png")
    m.close()


if __name__ == "__main__":
    # main()
    # plot()
    workflow(sys.argv[1], sys.argv[2])
