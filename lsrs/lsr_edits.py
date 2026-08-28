"""Sigh, process one off edits provided by the bureau in a spreadsheet."""

import re
import sys

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from sqlalchemy.engine import Connection

UTC_RE = re.compile(r"\d\d:\d\d\s+UTC")
LOCATION_RE = re.compile(r"\d\d.\d+N \d+.\d+W")
PROMPT = (
    "\n"
    "1. Skip [default]\n"
    "2 [idx] [repeat]. Update the Timestamp at index with %(newvalid)s\n"
    "3 [idx] [repeat]. Update the Location at index with %(lon)s %(lat)s\n"
    "4 [idx] [repeat]. Location to %(lon)s %(lat)s Time to %(newvalid)s\n"
    "D [idx] [repeat]. Delete at index\n"
)


def process(conn: Connection, row: dict) -> bool:
    """Process this row."""
    # Can we find the LSR?
    dbentries = pd.read_sql(
        sql_helper(
            """
        select typetext, ctid, city, county, coalesce(remark, '') as remark,
        st_x(geom) as lon, st_y(geom) as lat
        from {table} WHERE wfo = :wfo
        and valid = :valid
        """,
            table=f"lsrs_{row['valid'].year}",
        ),
        conn,
        params={"wfo": row["wfo"], "valid": row["valid"]},
    )

    # Can we glean a common ask to update the timestamp
    m = UTC_RE.search(row["Ask"])
    newvalid = None
    if m is not None:
        tokens = m.group(0).split(":")
        newvalid = row["valid"].replace(
            hour=int(tokens[0]), minute=int(tokens[1].split()[0])
        )
    # Can we find a location to update the LSR?
    m = LOCATION_RE.search(row["Ask"])
    lat = None
    lon = None
    if m is not None:
        tokens = m.group(0).split()
        lat = float(tokens[0][:-1])
        lon = float(tokens[1][:-1]) * -1.0

    print(f"Asking for: `{row['Ask']}`")
    print(f"    {row['T']} {row['City']} {row['County']} {row['valid']}\n")

    if dbentries.empty:
        print("No LSR found...")
    else:
        for idx, dbentry in dbentries.iterrows():
            print(
                f"{idx} {dbentry['typetext']:12s} {dbentry['city']:24s} "
                f"{dbentry['county']:24s} {dbentry['remark'][:50]}..."
            )

    # What do you want to do
    action = input(PROMPT % {"newvalid": newvalid, "lon": lon, "lat": lat})
    if action == "1" or action == "":
        return True
    action_tokens = action.split()
    updateidx = int(action_tokens[1])
    if action.startswith("2"):
        print("Updating timestamp of idx {} to {}".format(updateidx, newvalid))
        lon = dbentries.at[updateidx, "lon"]
        lat = dbentries.at[updateidx, "lat"]
    elif action.startswith("3"):
        print(
            "Updating location of idx {} to {} {}".format(updateidx, lon, lat)
        )
        newvalid = row["valid"]
    elif action.startswith("4"):
        print(
            "Updating location of idx {} to {} {} and time to {}".format(
                updateidx, lon, lat, newvalid
            )
        )
    elif action.startswith("D"):
        print("Deleting idx {}".format(updateidx))
        res = conn.execute(
            sql_helper(
                """
delete from {table} WHERE ctid = :ctid
            """,
                table=f"lsrs_{row['valid'].year}",
            ),
            {"ctid": dbentries.at[updateidx, "ctid"]},
        )
        conn.commit()
        return len(action_tokens) == 2
    else:
        print("Invalid choice, skipping.")
        return True

    res = conn.execute(
        sql_helper(
            """
update {table} SET valid = :valid, geom = ST_Point(:lon, :lat, 4326)
WHERE ctid = :ctid
        """,
            table=f"lsrs_{row['valid'].year}",
        ),
        {
            "valid": newvalid,
            "lon": lon,
            "lat": lat,
            "ctid": dbentries.at[updateidx, "ctid"],
        },
    )
    if res.rowcount != 1:
        print("DB FAIL")
        sys.exit()
    conn.commit()
    return len(action_tokens) == 2


@click.command()
@click.option(
    "--filename",
    required=True,
    help="Path to the spreadsheet file containing edits.",
)
@click.option("--wfo", required=True, help="The WFO that sent this.")
@click.option(
    "--start", type=int, default=0, help="Spreadsheet index to start"
)
def main(filename: str, wfo: str, start: int):
    """Process the edits from the given spreadsheet file."""
    lsrdf = pd.read_excel(filename)
    # Merge the Date and Time columns into a single UTC timestamp col
    lsrdf["valid"] = pd.to_datetime(
        lsrdf["Date"].astype(str) + " " + lsrdf["Time"].astype(str), utc=True
    )
    lsrdf["wfo"] = wfo
    with get_sqlalchemy_conn("postgis") as conn:
        for idx, row in lsrdf.iterrows():
            print(f"-----\n|  {idx}\n-------------------------------")
            if idx < start:
                print(f"Skipping {idx} due to start: {start}")
                continue
            # Recursion
            while not process(conn, row):
                pass


if __name__ == "__main__":
    main()
