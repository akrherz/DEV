"""Dump tornado warnings whose first LSR came 30+ minutes into the warning"""

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def get_misses(pgconn):
    """Our orig dataset."""
    return read_sql(
        """
        with tornadowarnings as (
            SELECT wfo, eventid, geom, issue, expire from sbw
            WHERE phenomena = 'TO'
            and significance = 'W' and status = 'NEW' and
            (expire - issue) >= '30 minutes'::interval   
        ), agg as (SELECT valid, w.wfo, w.eventid, w.issue, w.expire from
            tornadowarnings w LEFT JOIN lsrs l on (l.type = 'T' and
            ST_Contains(w.geom, l.geom)
            and l.valid >= w.issue and l.valid < w.expire and
            w.wfo = l.wfo and (w.expire - w.issue) >= '30 minutes'::interval)
            ORDER by w.wfo, w.issue)
        select wfo, extract(year from issue) as year, count(*) from agg
        WHERE valid is null GROUP by wfo, year ORDER by wfo, year
    """,
        pgconn,
        index_col=None,
    )


def get_hits(pgconn):
    """Our orig dataset."""
    return read_sql(
        """
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
    """,
        pgconn,
        index_col=None,
    )


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis")
    df = get_misses(pgconn)
    df.to_csv("misses.csv")


if __name__ == "__main__":
    main()
