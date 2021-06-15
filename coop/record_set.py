"""consec days"""
import datetime

from pyiem.util import get_dbconn
from pyiem.reference import state_names
from pyiem.network import Table as NetworkTable


def run_station(station):
    """Run for a station."""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    cursor.execute(
        """
    select sday, day, high, low from alldata_co WHERE station = %s
    and high is not null and low is not null ORDER by day ASC
    """,
        (station,),
    )
    records = {}
    returndate = None
    for row in cursor:
        record = records.setdefault(row[0], {"high": row[2], "low": row[3]})
        if row[2] >= record["high"] and row[3] <= record["low"]:
            # print(row)
            returndate = row[1]
        if row[2] >= record["high"]:
            record["high"] = row[2]
        if row[3] <= record["low"]:
            record["low"] = row[3]
    return returndate


def main():
    """Go Main Go"""
    for state in state_names:
        nt = NetworkTable(f"{state}CLIMATE")
        maxval = datetime.date(2000, 1, 1)
        for station in nt.sts:
            if station[2] != "T":
                continue
            date = run_station(station)
            if date is not None and date > maxval:
                print(f"{station} {date}")
                # maxval = date


if __name__ == "__main__":
    main()
