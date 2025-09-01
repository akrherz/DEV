"""Look at what we have for COOP valid and update accordingly."""

# third party
from pandas.io.sql import read_sql
from pyiem.database import get_dbconn


def main():
    """Go Main Go."""
    xref = read_sql(
        "select t.iemid, t.id, t.temp24_hour, t.precip24_hour, a.value from "
        "stations t JOIN station_attributes a ON (t.iemid = a.iemid) "
        "WHERE t.network ~* 'CLIMATE' and a.attr = 'TRACKS_STATION'",
        get_dbconn("mesosite"),
        index_col="iemid",
    )
    # See what iemaccess has
    access = read_sql(
        "SELECT distinct t.id || '|' || t.network as datum, "
        "extract(hour from s.coop_valid at time zone t.tzname)::int as hour "
        "from summary_2021 s JOIN stations t on (s.iemid = t.iemid) WHERE "
        "s.day > '2021-09-01' and s.coop_valid is not null",
        get_dbconn("iem"),
        index_col="datum",
    )
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    for iemid, row in xref.iterrows():
        if row["value"] not in access.index:
            continue
        minval = int(access.loc[row["value"]]["hour"].min())
        maxval = int(access.loc[row["value"]]["hour"].max())
        if minval == maxval:
            newval = minval
        elif (maxval - minval) < 4:  # some jitter with reports
            newval = minval + 1
        else:
            # Indeterminate
            continue
        if row["temp24_hour"] == newval and row["precip24_hour"] == newval:
            continue
        print(f"{row['id']} {row['precip24_hour']} -> {newval}")
        cursor.execute(
            "UPDATE stations SET temp24_hour = %s, precip24_hour = %s where "
            "iemid = %s",
            (newval, newval, iemid),
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
