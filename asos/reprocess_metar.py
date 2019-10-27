"""
 Reprocess RAW METAR data stored in the database, so to include more fields
"""
from __future__ import print_function
import datetime

from metar.Metar import Metar
from pyiem.util import get_dbconn, utc


def trace(val):
    if val.value("IN") == 0:
        return 0.0001
    return val.value("IN")


def main():
    """Go Main Go"""
    pgconn = get_dbconn("asos")
    icursor = pgconn.cursor()
    icursor2 = pgconn.cursor()

    sts = utc(2019, 1, 18)
    ets = utc(2019, 1, 21)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        icursor.execute(
            """
      select valid, station, metar from t"""
            + str(now.year)
            + """
      where metar is not null and valid >= %s and valid < %s
      and metar ~* ' I[0-9]{4}'
        """,
            (now, now + interval),
        )
        total = 0
        for row in icursor:
            try:
                mtr = Metar(row[2], row[0].month, row[0].year)
            except Exception as _exp:
                continue
            sql = "update t%s SET " % (now.year,)
            if mtr.ice_accretion_1hr:
                sql += "ice_accretion_1hr = %s," % (
                    trace(mtr.ice_accretion_1hr),
                )
            if mtr.ice_accretion_3hr:
                sql += "ice_accretion_3hr = %s," % (
                    trace(mtr.ice_accretion_3hr),
                )
            if mtr.ice_accretion_6hr:
                sql += "ice_accretion_6hr = %s," % (
                    trace(mtr.ice_accretion_6hr),
                )
            if sql == "update t%s SET " % (now.year,):
                continue
            sql = "%s WHERE station = '%s' and valid = '%s'" % (
                sql[:-1],
                row[1],
                row[0],
            )
            print(sql)
            icursor2.execute(sql)
            total += 1
            if total % 100 == 0:
                print("Done total: %s now: %s" % (total, now))
                pgconn.commit()
        now += interval
    icursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
