"""Dump tornado warnings whose first LSR came 30+ minutes into the warning"""

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn('postgis')
    df = read_sql("""
        with tornadowarnings as (
            SELECT wfo, eventid, geom, issue, expire from sbw
            WHERE phenomena = 'TO'
            and significance = 'W' and status = 'NEW' and
            (expire - issue) >= '30 minutes'::interval   
        ), mylsrs as (
            SELECT valid, w.wfo, w.eventid, w.issue, w.expire from
            lsrs l, tornadowarnings w WHERE l.type = 'T' and
            ST_Contains(w.geom, l.geom)
            and l.valid >= w.issue and l.valid < w.expire and
            w.wfo = l.wfo
        ), agg as (
            SELECT wfo, eventid, issue, expire, min(valid) as first
            from mylsrs GROUP by wfo, eventid, issue, expire
        )
        select *, extract(year from issue) as year
        from agg where (first - issue) >= '30 minutes'::interval
        ORDER by issue
    """, pgconn, index_col=None)
    df.to_csv('events.csv')


if __name__ == '__main__':
    main()
