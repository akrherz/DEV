"""Review our dual listed DCP and COOP sites."""
import subprocess

from pyiem.reference import state_names
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql

SCRIPT = "/opt/iem/scripts/dbutil/delete_station.py"


def delete(station, network):
    """Drop the station!"""
    cmd = f"python {SCRIPT} {network} {station}"
    subprocess.call(cmd, shell=True)


def main():
    """Go Main Go."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    ipgconn = get_dbconn("iem")
    for state in state_names:
        cursor.execute(
            "with data as (select id, count(*) from stations where "
            "network in (%s, %s) GROUP by id) "
            "select id from data where count = 2 ORDER by id",
            (f"{state}_DCP", f"{state}_COOP"),
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
                print(f"No Daily Data, droping COOP of {nwsli}")
                delete(nwsli, f"{state}_COOP")
            if "HG" in df["physical_code"].unique():
                print(df)
            # res = input("Delete COOP? (just enter)")


if __name__ == "__main__":
    main()
