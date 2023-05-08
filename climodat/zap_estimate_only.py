"""Remove realtime status for sites that are getting 100% estimates.

We generally do not want to have climodat realtime stations that are purely
estimated for one of the variables.  Some sites only report temp or precip
for example.  This script will remove realtime status for such sites.
"""

from pandas.io.sql import read_sql
from pyiem.reference import state_names
from pyiem.util import get_dbconn, get_sqlalchemy_conn


def do(ccursor, mcursor, state):
    """Do great things."""
    with get_sqlalchemy_conn("coop") as conn:
        df = read_sql(
            "select station, "
            "sum(case when temp_estimated then 1 else 0 end) as testimated, "
            "sum(case when precip_estimated then 1 else 0 end) as pestimated, "
            "count(*) as obs "
            f"from alldata_{state} where day > now() - '1 year'::interval and "
            "substr(station, 3, 1) not in ('T', 'C') and "
            "substr(station, 3, 4) != '0000' GROUP by station",
            conn,
            index_col="station",
        )
    df2 = df.query("obs == testimated or obs == pestimated")
    for station in df2.index.values:
        # Set online to false in mesosite
        mcursor.execute(
            "UPDATE stations SET online = 'f' WHERE id = %s", (station,)
        )
        # Truncate alldata for this station and year
        ccursor.execute(
            f"DELETE from alldata_{state} WHERE station = %s and year = 2022",
            (station,),
        )
        print(f"Culling {ccursor.rowcount} rows for last data for {station}")


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

    # Now remove any COOP tracking status for removed sites
    mcursor = mesositedb.cursor()
    mcursor.execute(
        "delete from station_attributes a USING stations t where "
        "a.iemid = t.iemid and attr = 'TRACKS_STATION' and not t.online"
    )
    print(f"Removed {mcursor.rowcount} COOP tracking from attributes")
    mcursor.close()
    mesositedb.commit()


if __name__ == "__main__":
    main()
