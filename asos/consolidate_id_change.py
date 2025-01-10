"""Hack things around in the database for when an ASOS ID changes."""

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from sqlalchemy import text


def create_meta_alias(meta, oldid, newid):
    """Add a station attribute."""
    with get_sqlalchemy_conn("mesosite") as conn:
        stmt = text(
            "INSERT INTO station_attributes (iemid, attr, value) "
            "VALUES (:newid, 'WAS', :oldid)"
        )
        res = conn.execute(
            stmt, {"newid": meta.loc[newid, "iemid"], "oldid": oldid}
        )
        print(f"{res.rowcount} rows inserted into WAS attr for {newid}")
        conn.commit()


def check_overlaps(oldid, newid):
    """Make sure we don't have trouble with overlapping obs."""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            text(
                "SELECT id, archive_begin, archive_end, iemid from stations "
                "WHERE id = ANY(:ids) and network ~* 'ASOS'"
            ),
            conn,
            params={"ids": [oldid, newid]},
            index_col="id",
        )
    # Possible a new id change, so archive_end may not be set
    if df.loc[oldid, "archive_end"] is None:
        df.loc[oldid, "archive_end"] = df.loc[newid, "archive_begin"]
    assert df.loc[oldid, "archive_end"] <= df.loc[newid, "archive_begin"]
    return df


def update_asosdb(oldid, newid):
    """Correct the station within the asos database."""
    with get_sqlalchemy_conn("asos") as conn:
        stmt = text(
            "UPDATE alldata SET station = :newid WHERE station = :oldid"
        )
        res = conn.execute(stmt, {"newid": newid, "oldid": oldid})
        # print the number of rows updated
        print(f"{res.rowcount} rows updated in asos db")
        conn.commit()


def update_iemaccess(meta, oldid, newid):
    """Update what we have in iemaccess."""
    # cull any summary rows after archive_end
    with get_sqlalchemy_conn("iem") as conn:
        stmt = text(
            "DELETE FROM summary WHERE iemid = :oldiemid and day > :lastdate"
        )
        res = conn.execute(
            stmt,
            {
                "oldiemid": meta.loc[oldid, "iemid"],
                "lastdate": meta.loc[oldid, "archive_end"],
            },
        )
        print(f"{res.rowcount} rows deleted from summary for {oldid}")
        # Delete anything in the summary table that is before the new
        # archive_begin
        # Update the iemid for the new id
        for tbl, col in zip(
            ["summary", "hourly"], ["day", "valid"], strict=True
        ):
            stmt = text(
                f"DELETE FROM {tbl} WHERE iemid = :newiemid and "
                f"{col} <= :lastdate"
            )
            res = conn.execute(
                stmt,
                {
                    "newiemid": meta.loc[newid, "iemid"],
                    "lastdate": meta.loc[oldid, "archive_end"],
                },
            )
            print(f"{res.rowcount} rows deleted from {tbl} for {newid}")
            stmt = text(
                f"UPDATE {tbl} SET iemid = :newiemid WHERE iemid = :oldiemid"
            )
            res = conn.execute(
                stmt,
                {
                    "newiemid": meta.loc[newid, "iemid"],
                    "oldiemid": meta.loc[oldid, "iemid"],
                },
            )
            print(f"{res.rowcount} rows {tbl} rows updated {oldid} -> {newid}")
        conn.commit()


@click.command()
@click.option("--oldid", help="Old ID")
@click.option("--newid", help="New ID")
def main(oldid, newid):
    """Do things."""
    meta = check_overlaps(oldid, newid)
    update_asosdb(oldid, newid)
    update_iemaccess(meta, oldid, newid)
    create_meta_alias(meta, oldid, newid)
    print("Considering SYNC_STATIONS.sh")


if __name__ == "__main__":
    main()
