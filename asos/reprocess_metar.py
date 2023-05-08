"""
 Reprocess RAW METAR data stored in the database, so to include more fields
"""
import datetime

from metar.Metar import Metar

from pyiem.reference import TRACE_VALUE
from pyiem.util import get_dbconn, logger, utc

LOG = logger()


def trace(val):
    """Special METAR logic for trace."""
    if val.value("IN") == 0:
        return TRACE_VALUE
    return val.value("IN")


def main():
    """Go Main Go"""
    pgconn = get_dbconn("asos")
    icursor = pgconn.cursor()
    icursor2 = pgconn.cursor()

    sts = utc(2006, 1, 1)
    ets = utc(2007, 1, 1)
    interval = datetime.timedelta(days=1)
    now = sts
    total = 0
    while now < ets:
        icursor.execute(
            f"select valid, station, metar from t{now.year} "
            "where metar is not null and valid >= %s and valid < %s "
            "and station = 'MSP' and wxcodes is null",
            (now, now + interval),
        )
        for row in icursor:
            try:
                mtr = Metar(row[2], row[0].month, row[0].year)
            except Exception as exp:
                LOG.exception(exp)
                continue
            if not mtr.weather:
                continue
            pwx = []
            for wx in mtr.weather:
                val = "".join([a for a in wx if a is not None])
                if val in ["", len(val) * "/"]:
                    continue
                pwx.append(val[:12])

            # LOG.info("%s %s -> %s", row[0], row[1], pwx)
            icursor2.execute(
                f"update t{now.year} SET wxcodes = %s WHERE station = %s "
                "and valid = %s",
                (pwx, row[1], row[0]),
            )
            total += 1
            if total % 100 == 0:
                LOG.info("Done total: %s now: %s", total, now)
                pgconn.commit()
                icursor2 = pgconn.cursor()
        now += interval
    icursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
