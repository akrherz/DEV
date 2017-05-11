"""Some stats based on distance from issuance time to issue

Flash Flood Watches are by Zone and Flash Flood Warnings are by County!
"""
import psycopg2
from tqdm import tqdm
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
import matplotlib.pyplot as plt


def workflow(wfo):
    """do work"""
    pgconn = psycopg2.connect(database='postgis', user='nobody', port=5555,
                              host='localhost')
    df = read_sql("""
    with counties as (
        select ugc, name, geom from ugcs where wfo = %s and
        substr(ugc, 3, 1) = 'C' and end_ts is null),
    zones as (
        select ugc, name, geom from ugcs where wfo = %s and
        substr(ugc, 3, 1) = 'Z' and end_ts is null and
        substr(ugc, 4, 3)::int < 300),
    -- assign every zone a primary county
    xref as (
        select c.ugc as county_ugc, z.ugc as zone_ugc
        from counties c JOIN zones z on
        (substr(c.ugc, 1, 2) = substr(z.ugc, 1, 2)
        and
        (st_area(ST_intersection(z.geom, c.geom)) / st_area(z.geom)) > 0.5)),
    mywatches as (
        SELECT product_issue, eventid, wfo, ugc, issue, expire, x.county_ugc
        from warnings w JOIN xref x on (w.ugc = x.zone_ugc)
        WHERE phenomena = 'FF' and significance = 'A' and wfo = %s
        and issue > '2006-01-01'),
    mywarnings as (
        SELECT wfo, ugc, issue, expire from warnings w
        WHERE phenomena = 'FF' and significance = 'W' and wfo = %s
        and issue > '2006-01-01'),
    agg1 as (
        SELECT a.wfo, a.eventid, a.ugc as watch_ugc, w.ugc as warn_ugc,
        a.product_issue, a.issue as watch_issue, a.expire as watch_expire,
        w.issue as warning_issue from mywatches a LEFT JOIN mywarnings w on
        (a.county_ugc = w.ugc
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
    """, pgconn, params=(wfo, wfo, wfo, wfo), index_col=None)
    if len(df.index) == 0:
        return None
    return len(df[df['warn_counties'] > 0].index) / float(len(df.index)) * 100.


def main():
    """Go Main"""
    nt = NetworkTable("WFO")
    rows = []
    for wfo in tqdm(nt.sts.keys()):
        rows.append(dict(wfo=wfo, freq=workflow(wfo)))
    df = pd.DataFrame(rows)
    df.to_csv('wfo.csv')


def plot():
    """Make a pretty plot"""
    df = pd.read_csv('wfo.csv')
    df.set_index('wfo', inplace=True)
    m = MapPlot(sector='conus',
                title="Percentage of Flash Flood Watches receiving 1+ FFW",
                subtitle='PRELIMINARY PLOT! Please do not share :)')
    cmap = plt.get_cmap('jet')
    df2 = df[df['freq'].notnull()]
    m.fill_cwas(df2['freq'].to_dict(), cmap=cmap, units='%',
                lblformat='%.0f', ilabel=True)
    m.postprocess(filename='test.png')
    m.close()


if __name__ == '__main__':
    # main()
    plot()
