"""Attempt to merge in old FFS,SVS data into warnings table!"""

import sys
from datetime import timedelta, timezone

from ingest_old_warnings import compute_until
from psycopg2.extras import DictCursor

from geopandas import read_postgis
from pyiem.database import get_dbconn
from pyiem.nws.products.vtec import parser
from pyiem.nws.vtec import VTEC
from pyiem.util import noaaport_text

FMT = "%y%m%dT%H%MZ"


def do_update(pcursor, df, v):
    """Update the database given what events we found."""
    # If we have duplicate ugcs, we likely have some troubles
    if len(df["ugc"].unique()) != len(df.index):
        print("Ambiguous Result.")
        print(df)
        return
    entry = df.iloc[0]
    phenomena = entry["phenomena"]
    significance = entry["significance"]
    # OYE, products could have gotten merged, sigh
    for eventid in df["eventid"].unique():
        v.segments[0].vtec = [
            VTEC(
                [
                    "",
                    "O",
                    "CON",
                    v.source,
                    phenomena,
                    significance,
                    eventid,
                    entry["issue"].astimezone(timezone.utc).strftime(FMT),
                    entry["expire"].astimezone(timezone.utc).strftime(FMT),
                ]
            )
        ]
        # IMPORTANT: keeps logic from finding a bad year :(
        v.segments[0].vtec[0].year = v.valid.year
        v.sql(pcursor)
        if v.warnings:
            print(str(v.segments[0].vtec[0]))
            print(v.warnings)


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    phenomena = argv[2]
    significance = argv[3]
    afosdb = get_dbconn("afos")
    postgisdb = get_dbconn("postgis")
    pcursor = postgisdb.cursor(cursor_factory=DictCursor)
    # Need polygons to come along for the ride to help with ambiquity
    events = read_postgis(
        "WITH polys as ("
        f"SELECT wfo, eventid, geom from sbw_{year} WHERE status = 'NEW' and "
        "phenomena = 'FF' and significance = 'W') "
        "SELECT ugc, w.wfo, w.eventid, issue, expire, geom, w.phenomena, "
        f"w.significance from warnings_{year} w LEFT JOIN polys p ON "
        "(w.wfo = p.wfo and w.eventid = p.eventid) "
        "WHERE phenomena = %s and significance = %s "
        "ORDER by w.wfo, eventid",
        postgisdb,
        params=(phenomena, significance),
        index_col=None,
        geom_col="geom",
    )
    events["year"] = year
    cursor = afosdb.cursor()
    cursor.execute(
        "SELECT data, entered from products where substr(pil, 1, 3) = 'FFS' "
        f"and entered > '{year}-01-01' and entered < '{year + 1}-01-01' "
        " and (data ~* 'FLASH FLOOD WARNING' or "
        "data ~* 'FLASH FLOOD EMERGENCY') "
        "ORDER by entered ASC"
    )
    for row in cursor:
        text = noaaport_text(row[0])
        utcnow = row[1].astimezone(timezone.utc)
        if text.find("TEST FLASH FLOOD WARNING") > -1:
            continue
        try:
            v = parser(text, utcnow=utcnow)
        except Exception as exp:
            print(exp)
            continue
        ugcs = [str(u) for u in v.segments[0].ugcs]
        if not ugcs:
            continue
        endts = compute_until(v)
        if endts is None:
            # Look if we can make a simple match
            df = events[
                (events["wfo"] == v.source[1:])
                & (events["issue"] <= v.valid)
                & ((events["expire"] + timedelta(minutes=60)) >= v.valid)
                & events["ugc"].isin(ugcs)
            ]
            if len(ugcs) == len(df["ugc"].unique()):
                do_update(pcursor, df, v)
                continue
        if endts is None:
            print(f"Failed to compute endts {v.get_product_id()}")
            continue
        # Ideally, we find an exact match
        df = events[
            (events["wfo"] == v.source[1:])
            & (events["issue"] <= v.valid)
            & (events["expire"] == endts)
            & events["ugc"].isin(ugcs)
        ]
        if len(ugcs) == len(df["ugc"].unique()):
            do_update(pcursor, df, v)
            continue
        # Loosen expire some more
        df = events[
            (events["wfo"] == v.source[1:])
            & (events["issue"] <= v.valid)
            & (events["expire"] > v.valid)
            & events["ugc"].isin(ugcs)
        ]
        if len(ugcs) == len(df["ugc"].unique()):
            do_update(pcursor, df, v)
            continue
        print(f"failed {v.get_product_id()}")
    pcursor.close()
    postgisdb.commit()


if __name__ == "__main__":
    main(sys.argv)
