"""The IEM summary table has a coop_valid column that tracks when the SHEF
COOP report was valid.  This was not around in the database from day1, so we
should backfill it"""

import datetime
import sys

import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import logger

LOG = logger()
IEM = get_dbconn("iem")
HADS = get_dbconn("hads")


def workflow(iemid, row):
    """Do Work."""
    # 1. Figure out dates we need to process
    hcursor = HADS.cursor()
    icursor = IEM.cursor()
    nwsli = row["id"]
    ts = datetime.datetime.now()
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
        SELECT day, max_tmpf, pday from summary WHERE iemid = %s
        and day < %s and (max_tmpf is not null or pday is not null)
        and coop_valid is null
        ORDER by day
        """,
            conn,
            params=(iemid, row["coop_valid_begin"]),
            index_col="day",
        )
    updated = 0
    for day, _ in df.iterrows():
        ts = ts.replace(year=day.year, month=day.month, day=day.day)
        hcursor.execute(
            f"""
        SELECT distinct extract(hour from valid)::int as hr
        from raw{day:%Y_%m} WHERE station = %s
        and valid between %s and %s and substr(key, 1, 2) in ('PP', 'TA')
        """,
            (
                nwsli,
                ts.replace(hour=0, minute=0),
                ts.replace(hour=23, minute=59),
            ),
        )
        hours = [a[0] for a in hcursor.fetchall()]
        if len(hours) != 1 or hours[0] == 0:
            continue
        # Update IEM access
        coopvalid = ts.replace(
            hour=hours[0], minute=0, second=0, microsecond=0
        )
        icursor.execute(
            f"UPDATE summary_{coopvalid.year} SET coop_valid = %s "
            "WHERE iemid = %s and day = %s",
            (coopvalid, iemid, day),
        )
        updated += 1

    LOG.info(
        "%s iemid:%s updated/found %s/%s", nwsli, iemid, updated, len(df.index)
    )
    icursor.close()
    IEM.commit()


def main(argv):
    """Go Main Go"""
    network = argv[1]
    # 1. Find stations in 2016 that reported a coop_valid
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
        SELECT min(day) as archive_begin,
        min(coop_valid) as coop_valid_begin,
        t.iemid, t.id from summary S JOIN stations t on (s.iemid = t.iemid)
        WHERE t.network = %s
        GROUP by t.iemid, t.id
        """,
            conn,
            params=(network,),
            index_col="iemid",
        )
    for iemid, row in df.iterrows():
        if row["coop_valid_begin"] is None:
            continue
        workflow(iemid, row)


if __name__ == "__main__":
    main(sys.argv)
