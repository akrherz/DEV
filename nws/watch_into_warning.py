"""Some stats based on distance from issuance time to issue

Flash Flood Watches are by Zone and Flash Flood Warnings are by County!
"""
import psycopg2
from pandas.io.sql import read_sql


def main():
    """Go Main"""
    pgconn = psycopg2.connect(database='postgis', user='nobody', port=5555,
                              host='localhost')
    wfo = 'FSD'
    df = read_sql("""
    with mywatches as (
        SELECT product_issue, eventid, w.wfo, w.ugc, issue, expire, u.geom
        from warnings w JOIN ugcs u on (w.gid = u.gid)
        WHERE phenomena = 'FF' and significance = 'A' and w.wfo = %s
        and issue > '2006-01-01'),
    mywarnings as (
        SELECT w.wfo, w.ugc, issue, expire, u.geom from warnings w JOIN
        ugcs u on (w.gid = u.gid)
        WHERE phenomena = 'FF' and significance = 'W' and w.wfo = %s
        and issue > '2006-01-01'),
    agg1 as (
        SELECT a.wfo, a.eventid, a.ugc as watch_ugc, w.ugc as warn_ugc,
        a.product_issue, a.issue as watch_issue, a.expire as watch_expire,
        w.issue as warning_issue from mywatches a LEFT JOIN mywarnings w on
        (substr(a.ugc, 1, 2) = substr(w.ugc, 1, 2) and
         (st_area(ST_intersection(a.geom, w.geom)) / st_area(a.geom)) > 0.8
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
    extract('epoch' from min(watch_issue) - min(product_issue)) / 60. as minutes,
    count(*) as watch_zones,
    sum(case when warning_issue is not null then 1 else 0 end) as warn_counties
    from agg2 GROUP by wfo, yr, eventid ORDER by yr ASC, eventid ASC
    """, pgconn, params=(wfo, wfo), index_col=None)
    df.to_csv('fsd.csv', index=False)


if __name__ == '__main__':
    main()
