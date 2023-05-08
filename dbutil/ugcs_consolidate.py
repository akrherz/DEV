"""Keep our ugcs database table from bloating.

The pain is so bad with this, see akrherz/pyIEM#387
"""

import pandas as pd
from pyiem.util import get_dbconn, get_sqlalchemy_conn, logger

LOG = logger()


def drop_gid(cursor, ugc, gid):
    """Remove this entry!"""
    # Update warnings table
    cursor.execute("UPDATE warnings SET gid = null WHERE gid = %s", (gid,))
    if cursor.rowcount > 0:
        LOG.info(
            "Set %s warning rows to null for %s %s",
            cursor.rowcount,
            ugc,
            gid,
        )
    # Remove entry
    cursor.execute("DELETE from ugcs where gid = %s", (gid,))
    # Update entries using crude logic for now
    cursor.execute(
        "UPDATE warnings SET gid = get_gid(ugc, issue) WHERE "
        "gid is null and ugc = %s",
        (ugc,),
    )


def cull_no_times(cursor):
    """Entries with begin_ts == end_ts are in error, cull them."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            "SELECT ugc, gid from ugcs where begin_ts = end_ts ORDER by ugc",
            conn,
            index_col=None,
        )
    LOG.info("Found %s rows for consideration", len(df.index))
    for _, row in df.iterrows():
        drop_gid(cursor, row["ugc"], row["gid"])


def dual_firewx_zone_collapse(pgconn, gdf, ugc):
    """Keep two entries around, if possible."""
    if len(gdf.index) == 2:
        return
    if len(gdf["name"].unique()) > 1:
        return
    if len(gdf["wfo"].unique()) > 1:
        return
    if abs(gdf["area2163"].max() - gdf["area2163"].min()) > 0.8:
        return
    cursor = pgconn.cursor()
    # Set entries to 1980 for non-null sources
    cursor.execute(
        "UPDATE ugcs SET begin_ts = '1980-01-01' WHERE ugc = %s and "
        "source is not null",
        (ugc,),
    )
    LOG.info("Removing %s rows for %s", len(gdf.index) - 2, ugc)
    for gid, row in gdf.iterrows():
        if row["source"] is not None:
            continue
        drop_gid(cursor, ugc, gid)
    cursor.close()
    pgconn.commit()


def backwards_collapse(pgconn, gdf, ugc, ascending):
    """Look back in time and see how far we can go."""
    df = gdf[gdf["source"].isna()]
    if len(df.index) == 1:
        return
    df = df.sort_values("begin_ts", ascending=ascending)
    depth = 1
    for i in range(0, len(df.index) - 1):
        df2 = df.iloc[0 : (i + 2)]
        # names are same
        if len(df2["name"].unique()) > 1:
            break
        if len(df2["wfo"].unique()) > 1:
            break
        if abs(df2["area2163"].max() - df2["area2163"].min()) > 0.8:
            break
        depth += 1
    if depth == 1:
        return
    df = df.iloc[:depth]
    cursor = pgconn.cursor()
    # Assume first entry is the best
    keepgid = int(df.index.values[0])
    LOG.info("Collapsing %s rows for %s keeping %s", depth, ugc, keepgid)
    if not ascending:
        # Update begin_ts for our keeper
        cursor.execute(
            "UPDATE ugcs SET begin_ts = %s WHERE gid = %s",
            (
                df["begin_ts"].min(),
                keepgid,
            ),
        )
    else:
        # Update end_ts for our keeper
        cursor.execute(
            "UPDATE ugcs SET end_ts = %s WHERE gid = %s",
            (
                df["end_ts"].max(),
                keepgid,
            ),
        )
    for gid in [int(i) for i in df.index.values]:
        if gid == keepgid:
            continue
        drop_gid(cursor, ugc, gid)
    cursor.close()
    pgconn.commit()


def simple_collapse(pgconn, gdf, ugc):
    """Simpliest logic."""
    if len(gdf["name"].unique()) > 1:
        return
    if len(gdf["wfo"].unique()) > 1:
        return
    if abs(gdf["area2163"].max() - gdf["area2163"].min()) > 0.8:
        return
    if len(gdf["source"].unique()) > 2:
        return
    cursor = pgconn.cursor()
    # Assume last entry is the best
    keepgid = int(gdf.index.max())
    # Update begin_ts for our keeper to 1980
    cursor.execute(
        "UPDATE ugcs SET begin_ts = '1980-01-01' WHERE gid = %s", (keepgid,)
    )
    LOG.info(
        "Removing %s rows for %s keeping gid %s",
        len(gdf.index) - 1,
        ugc,
        keepgid,
    )
    for gid in [int(i) for i in gdf.index.values]:
        if gid == keepgid:
            continue
        drop_gid(cursor, ugc, gid)
    cursor.close()
    pgconn.commit()


def collapse(pgconn):
    """Find UGCs that can easily be collapsed."""
    # Requirements for equality
    # name, wfo, area2163 <1sqkm, source=1
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            "SELECT ugc, gid, begin_ts, end_ts, source, area2163, name, "
            "wfo from ugcs ORDER by ugc ASC, begin_ts ASC",
            conn,
            index_col="gid",
        )
    LOG.info("loaded %s ugcs entries", len(df.index))
    for ugc, gdf in df.groupby("ugc"):
        if len(gdf.index) == 1:
            continue
        # simple_collapse(pgconn, gdf, ugc)
        # dual_firewx_zone_collapse(pgconn, gdf, ugc)
        for mydir in [True, False]:
            backwards_collapse(pgconn, gdf, ugc, mydir)


def main():
    """Things that we can do."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    # cull_no_times(cursor)
    collapse(pgconn)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
