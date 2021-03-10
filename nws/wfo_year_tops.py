"""Unsure."""

# third party
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn

pgconn = get_dbconn("postgis")
nt = NetworkTable("WFO")

df = read_sql(
    """
with data as (select wfo, phenomena, eventid, extract(year from issue) as yr
 from sbw WHERE status = 'NEW' and phenomena in ('SV', 'TO')
 and significance = 'W'),
 agg as (select wfo, yr, phenomena, count(*) from data
 GROUP by wfo, yr, phenomena),
 agg2 as (select wfo, yr, phenomena, count, rank()
 OVER (PARTITION by yr, phenomena ORDER by count DESC) from agg)
 SELECT wfo, yr::int as year, phenomena, count from agg2 where rank = 1
 ORDER by year, phenomena""",
    pgconn,
    index_col=None,
)

svr = df[df["phenomena"] == "SV"].copy(True).set_index("year")
tor = df[df["phenomena"] == "TO"].copy(True).set_index("year")

for year in svr.index.values:
    print(
        ("  %s  %3i %s %-18s  ||  %3i %s %-18s")
        % (
            year,
            svr.at[year, "count"],
            svr.at[year, "wfo"],
            nt.sts[svr.at[year, "wfo"]]["name"],
            tor.at[year, "count"],
            tor.at[year, "wfo"],
            nt.sts[tor.at[year, "wfo"]]["name"],
        )
    )
