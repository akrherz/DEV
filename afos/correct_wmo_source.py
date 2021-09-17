"""Rectify some old WMO source codes used.

Archives of text data have been processed by the IEM.  Products prior to
NWS modernization (early 2000s) used a mixture of WMO source codes.  These
codes are important to various apps.  So this script attempts to fix it.

Attempts to create lookups for one-off CLI products
with data as (
    select distinct source, pil from products_1999_0106),
 agg as (
     select source, count(*), max(pil) from data GROUP by source),
 agg2 as (
     select * from agg where count = 1 and substr(max, 1, 3) = 'CLI')

 select distinct '"'||a.source||'": "'||c.source||'",'
 from products_2018_0712 c, agg2 a WHERE c.pil = a.max;

 with data as (
     select distinct pil from products_2009_0106 where source is null),
 present as (
     select distinct c.source, d.pil from products_2018_0712 c, data d
     where c.pil = d.pil)
 update products_2009_0106 t SET source = p.source
 FROM present p WHERE t.source is null and t.pil = p.pil;
"""
import sys

from pyiem.util import get_dbconn
from pandas.io.sql import read_sql

# Pull in the standardized conversion
sys.path.insert(0, "/opt/iem/scripts/util")
from poker2afos import XREF_SOURCE  # noqa


def fixer(pgconn, oldval, newval):
    """Update database."""
    cursor = pgconn.cursor()
    cursor.execute(
        "UPDATE products SET source = %s WHERE source = %s", (newval, oldval)
    )
    print(f"Correcting {oldval} -> {newval}, {cursor.rowcount} rows")
    cursor.close()
    pgconn.commit()


def do_table(pgconn, table):
    """Go Main Go."""
    df = read_sql(
        f"SELECT source, count(*) from {table} "
        "WHERE source is not null GROUP by source ORDER by source",
        pgconn,
        index_col="source",
    )
    for source in df.index.values:
        newsource = XREF_SOURCE.get(source, source)
        if newsource == source:
            continue
        fixer(pgconn, source, newsource)


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    for year in range(1983, 2021):
        for suffix in ["0106", "0712"]:
            do_table(pgconn, f"products_{year}_{suffix}")


if __name__ == "__main__":
    main()
