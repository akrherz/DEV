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
import json

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql

# Pull in the standardized conversion
sys.path.insert(0, "/opt/iem/scripts/util")
from poker2afos import XREF_SOURCE


def fixer(pgconn, oldval, newval):
    """Update database."""
    cursor = pgconn.cursor()
    cursor.execute(
        "UPDATE products SET source = %s WHERE source = %s", (newval, oldval)
    )
    print(("Correcting %s -> %s, %s rows") % (oldval, newval, cursor.rowcount))
    cursor.close()
    pgconn.commit()


def main(argv):
    """Go Main Go."""
    table = argv[1]
    nt = NetworkTable(["WFO", "RFC", "NWS", "NCEP", "CWSU", "WSO"])
    pgconn = get_dbconn("afos")
    mpgconn = get_dbconn("mesosite")
    mcursor = mpgconn.cursor()
    df = read_sql(
        f"SELECT source, count(*) from {table} "
        "WHERE source is not null GROUP by source ORDER by source",
        pgconn,
        index_col="source",
    )
    updated = False
    for source, row in df.iterrows():
        if source[0] not in ["K", "P"]:
            continue
        iemsource = source[1:] if source[0] == "K" else source
        if iemsource in nt.sts:
            continue
        if source in XREF_SOURCE:
            fixer(pgconn, source, XREF_SOURCE[source])
            continue
        if row["count"] < 10:
            print("skipping %s as row count is low" % (source,))
            continue
        mcursor.execute(
            "SELECT wfo from stations where id = %s and network ~* 'ASOS' "
            "and wfo is not null",
            (iemsource,),
        )
        if mcursor.rowcount == 0:
            print("Source: %s is double unknown" % (source,))
            continue
        newval = mcursor.fetchone()[0]
        newval = f"P{newval}" if source[0] == "P" else f"K{newval}"
        print("would assign %s to %s" % (source, newval))
        XREF_SOURCE[source] = newval
        fixer(pgconn, source, XREF_SOURCE[source])
        updated = True

    if updated:
        print(json.dumps(XREF_SOURCE, indent=4, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
