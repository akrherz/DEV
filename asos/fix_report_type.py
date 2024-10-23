"""Sometimes stations had varying reset times.

See akrherz/iem#104
"""

import click
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import logger

LOG = logger()
ATTR = "METAR_RESET_MINUTE"


def do(year, station, total):
    """Process this network."""
    remaining = total
    # Get the minute of the hour that the station resets
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "select value from station_attributes a JOIN stations t "
        "on (a.iemid = t.iemid) WHERE t.id = %s and a.attr = %s",
        (station, ATTR),
    )
    minute = None
    if cursor.rowcount == 0:
        LOG.info("Missing %s", station)
    else:
        minute = cursor.fetchone()[0]
    pgconn.close()

    # Low hanging fruit first.
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    cursor.execute(
        f"""
        update t{year} SET report_type = 3 WHERE station = %s
        and extract(minute from valid) = %s and report_type = 2
        """,
        (station, minute),
    )
    LOG.info("%s[%s] %s -> 2 to 3", station, year, cursor.rowcount)
    remaining -= cursor.rowcount
    if remaining > 0:
        cursor.execute(
            f"""
            update t{year} SET report_type = 4 WHERE station = %s
            and report_type = 2
            """,
            (station,),
        )
        LOG.info("%s[%s] %s -> 2 to 4", station, year, cursor.rowcount)
    cursor.close()
    pgconn.commit()
    pgconn.close()


@click.command()
@click.option("--year", required=True, type=int, help="Year to process")
def main(year):
    """Go Main Go."""
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            "SELECT station, count(*) from alldata where valid >= %s and "
            "valid < %s and report_type = 2 group by station",
            conn,
            index_col="station",
            params=(f"{year}-01-01 00:00+00", f"{year+1}-01-01 00:00+00"),
        )
    LOG.info("Found %s stations and %s rows", len(df.index), df["count"].sum())
    for station in df.index:
        do(year, station, df.at[station, "count"])


if __name__ == "__main__":
    main()
