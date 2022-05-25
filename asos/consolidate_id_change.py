"""Hack things around in the database for when an ASOS ID changes."""
# Stlib
import sys

# third party
from sqlalchemy import text
import pandas as pd
from pyiem.util import get_sqlalchemy_conn


def check_overlaps(oldid, newid):
    """Make sure we don't have trouble with overlapping obs."""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            text(
                "SELECT id, archive_begin, archive_end, iemid from stations "
                "WHERE id in :ids and network ~* 'ASOS'"
            ),
            conn,
            params={"ids": tuple([oldid, newid])},
            index_col="id",
        )
    assert df.loc[oldid, "archive_end"] < df.loc[newid, "archive_begin"]
    return df


def update_asosdb(oldid, newid):
    """Correct the station within the asos database."""
    with get_sqlalchemy_conn("asos") as conn:
        stmt = text(
            "UPDATE alldata SET station = :newid WHERE station = :oldid"
        )
        res = conn.execute(stmt, newid=newid, oldid=oldid)
        # print the number of rows updated
        print(f"{res.rowcount} rows updated in asos db")


def update_iemaccess(meta, oldid, newid):
    """Update what we have in iemaccess."""
    # cull any summary rows after archive_end
    with get_sqlalchemy_conn("iem") as conn:
        stmt = text(
            "DELETE FROM summary WHERE iemid = :oldiemid and "
            "day > :lastdate"
        )
        res = conn.execute(
            stmt,
            oldiemid=meta.loc[oldid, "iemid"],
            lastdate=meta.loc[oldid, "archive_end"],
        )
        print(f"{res.rowcount} rows deleted from summary for {oldid}")
        # Delete anything in the summary table that is before the new
        # archive_begin
        stmt = text(
            "DELETE FROM summary WHERE iemid = :newiemid and "
            "day <= :lastdate"
        )
        res = conn.execute(
            stmt,
            newiemid=meta.loc[newid, "iemid"],
            lastdate=meta.loc[oldid, "archive_end"],
        )
        print(f"{res.rowcount} rows deleted from summary for {newid}")
        # Update the iemid for the new id
        stmt = text(
            "UPDATE summary SET iemid = :newiemid WHERE iemid = :oldiemid"
        )
        res = conn.execute(
            stmt,
            newiemid=meta.loc[newid, "iemid"],
            oldiemid=meta.loc[oldid, "iemid"],
        )
        print(f"{res.rowcount} rows summary rows updated {oldid} -> {newid}")


def main(argv):
    """Do things."""
    oldid = argv[1]
    newid = argv[2]
    meta = check_overlaps(oldid, newid)
    update_asosdb(oldid, newid)
    update_iemaccess(meta, oldid, newid)
    print("Considering running dbutil/delete_stations.py")


if __name__ == "__main__":
    main(sys.argv)
