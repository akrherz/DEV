"""Compute daily rstage min and max, when necessary."""

import datetime
import sys

import pytz

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, logger, utc

LOG = logger()


def workflow(date):
    """Do the necessary work for this date"""
    pgconn = get_dbconn("hads")
    iem_pgconn = get_dbconn("iem")
    # Load up our PEDTS dictionary
    with get_dbconn("mesosite") as dbconn:
        df = read_sql(
            "SELECT id, t.iemid, tzname, value as pedts from stations t JOIN "
            "station_attributes a on (t.iemid = a.iemid) "
            "WHERE a.attr = 'PEDTS'",
            dbconn,
            index_col="id",
        )
    bases = {}
    ts = utc(date.year, date.month, date.day, 12)
    for tzname in df["tzname"].unique():
        base = ts.astimezone(pytz.timezone(tzname))
        bases[tzname] = base.replace(hour=0)
    # retrieve data that is within 12 hours of our bounds
    sts = datetime.datetime(
        date.year, date.month, date.day
    ) - datetime.timedelta(hours=12)
    ets = sts + datetime.timedelta(hours=48)
    keys = df["pedts"].str.slice(0, 3).unique().tolist()
    obsdf = read_sql(
        f"""
    SELECT distinct station, valid at time zone 'UTC' as utc_valid, key, value
    from raw{date.year} WHERE valid between %s and %s and
    substr(key, 1, 3) in %s and value >= 0
    """,
        pgconn,
        params=(sts, ets, tuple(keys)),
        index_col=None,
    )
    if obsdf.empty:
        LOG.info("%s found no data", date)
        return
    obsdf["utc_valid"] = obsdf["utc_valid"].dt.tz_localize(pytz.UTC)
    for station, gdf in obsdf.groupby("station"):
        if station not in df.index:
            continue
        colname = f"{df.at[station, 'pedts']}Z"
        # Find the data for the local valid date
        sts = bases[df.at[station, "tzname"]]
        ets = sts + datetime.timedelta(hours=24)
        df3 = gdf[
            (gdf["key"] == colname)
            & (gdf["utc_valid"] > sts)
            & (gdf["utc_valid"] <= ets)
        ]
        if df3.empty:
            continue
        minval = df3["value"].min()
        maxval = df3["value"].max()
        iemid = df.at[station, "iemid"]
        icursor = iem_pgconn.cursor()
        icursor.execute(
            f"SELECT min_rstage, max_rstage from summary_{date.year} "
            "WHERE iemid = %s and day = %s",
            (iemid, date),
        )
        if icursor.rowcount == 0:
            LOG.info("Adding record %s[%s] for day %s", station, iemid, date)
            icursor.execute(
                f"INSERT into summary_{date.year} (iemid, day) "
                "VALUES (%s, %s) RETURNING min_rstage, max_rstage",
                (iemid, date),
            )
        (current_minval, current_maxval) = icursor.fetchone()
        if (
            current_minval is not None
            and current_maxval is not None
            and minval >= current_minval
            and maxval <= current_maxval
        ):
            continue
        LOG.debug("%s %s %s", station, minval, maxval)
        icursor.execute(
            f"UPDATE summary_{date.year} "
            "SET min_rstage = %s, max_rstage = %s WHERE "
            "iemid = %s and day = %s",
            (minval, maxval, iemid, date),
        )
        icursor.close()
        iem_pgconn.commit()


def main(argv):
    """Do Something"""
    if len(argv) == 4:
        ts = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    else:
        ts = datetime.date.today()
    workflow(ts)


if __name__ == "__main__":
    main(sys.argv)
