"""Review our dual listed DCP and COOP sites."""

import subprocess

from pandas.io.sql import read_sql
from pyiem.database import get_dbconn
from pyiem.reference import state_names

SCRIPT = "/opt/iem/scripts/dbutil/delete_station.py"


def delete(station, network):
    """Drop the station!"""
    cmd = f"python {SCRIPT} {network} {station}"
    subprocess.call(cmd, shell=True)


def move(cursor, nwsli, state):
    """Move to DCP"""
    cursor.execute(
        "UPDATE stations SET network = %s where id = %s and " "network = %s",
        (f"{state}_DCP", nwsli, f"{state}_COOP"),
    )


def main():
    """Go Main Go."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    ipgconn = get_dbconn("iem")
    for state in state_names:
        cursor2 = pgconn.cursor()
        cursor.execute(
            "with data as (select id, count(*), max(network) from stations "
            "where network in (%s, %s) GROUP by id) "
            "select id from data where count = 1 and max = %s ORDER by id",
            (f"{state}_DCP", f"{state}_COOP", f"{state}_COOP"),
        )
        for row in cursor:
            nwsli = row[0]
            df = read_sql(
                "SELECT * from current_shef where station = %s ORDER by valid",
                ipgconn,
                params=(nwsli,),
            )
            # If there is no 'D' in duration column
            if "D" not in df["duration"].unique():
                print(f"No Daily Data, moving {nwsli} to DCP")
                # print(df)
                move(cursor2, nwsli, state)
            # if "HG" in df["physical_code"].unique():
            #    print(df)
            # res = input("Delete COOP? (just enter)")
        cursor2.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
