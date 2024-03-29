"""Remove realtime status for sites that are getting 100% estimates.

We generally do not want to have climodat realtime stations that are purely
estimated for one of the variables.  Some sites only report temp or precip
for example.  This script will remove realtime status for such sites.

Note: This is chunking a year at a time, attm.
"""

import pandas as pd
from pyiem.reference import state_names
from pyiem.util import get_dbconn, get_sqlalchemy_conn


def do(ccursor, mcursor, state):
    """Do great things."""
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
            select station,
            sum(case when temp_estimated then 1 else 0 end) as testimated,
            sum(case when precip_estimated then 1 else 0 end) as pestimated,
            count(*) as obs
            from alldata_{state} where year = 2023 and
            substr(station, 3, 1) not in ('T', 'C', 'D', 'K') and
            substr(station, 3, 4) != '0000' GROUP by station
            """,
            conn,
            index_col="station",
        )
    df2 = df.query("obs == testimated or obs == pestimated")
    for station in df2.index.values:
        # Set online to false in mesosite
        mcursor.execute(
            """
            UPDATE stations SET online = 'f', archive_end = '2022-12-31'
            WHERE id = %s and network = %s and online
            """,
            (station, f"{state}CLIMATE"),
        )
        # Truncate alldata for this station and year
        ccursor.execute(
            "DELETE from alldata WHERE station = %s and year = 2023",
            (station,),
        )
        print(f"Culled {ccursor.rowcount} rows for {station}")


def main():
    """Workflow."""
    coopdb = get_dbconn("coop")
    mesositedb = get_dbconn("mesosite")
    for state in state_names:
        ccursor = coopdb.cursor()
        mcursor = mesositedb.cursor()
        do(ccursor, mcursor, state)
        ccursor.close()
        mcursor.close()
        coopdb.commit()
        mesositedb.commit()


if __name__ == "__main__":
    main()
