"""
Reprocess RAW METAR data stored in the database, so to include more fields
"""

import re
from datetime import timedelta, timezone

from metar.Metar import Metar, ParserError
from pyiem.reference import TRACE_VALUE
from pyiem.util import get_dbconn, logger, utc

LOG = logger()
UNPARSED = re.compile(r"Unparsed groups in body '([^']*)'", re.IGNORECASE)


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

    sts = utc(2019, 4, 17)
    ets = utc(2019, 4, 18)
    interval = timedelta(days=1)
    now = sts
    total = 0
    while now < ets:
        icursor.execute(
            f"select valid, station, metar from t{now.year} "
            "where valid >= %s and valid < %s "
            "and station = 'DSM' and peak_wind_gust is null and "
            "strpos(metar, ' PK WND') > 0",
            (now, now + interval),
        )
        for row in icursor:
            mtrtext = row[2]
            # Try and try again
            for attempt in range(5):
                try:
                    mtr = Metar(mtrtext, row[0].month, row[0].year)
                except ParserError as exp:
                    errmsg = str(exp)
                    m = UNPARSED.search(errmsg)
                    if m:
                        trouble = m.group(1)
                        LOG.warning(
                            "Attempt: %s/5 Removing %s from trouble: %s",
                            attempt + 1,
                            trouble,
                            mtrtext,
                        )
                        mtrtext = mtrtext.replace(f" {trouble}", "")
                        continue
                    break
            if mtr.wind_speed_peak is None:
                LOG.warning(
                    "No peak wind gust for %s %s %s",
                    row[0],
                    row[1],
                    row[2],
                )
                continue
            peak_wind_gust = mtr.wind_speed_peak.value("KT")
            peak_wind_drct = mtr.wind_dir_peak.value()
            peak_wind_time = mtr.peak_wind_time.replace(tzinfo=timezone.utc)
            if (
                peak_wind_drct > 360
                or peak_wind_gust > 120
                or peak_wind_time > row[0]
            ):
                LOG.warning(
                    "Bad peak wind data for %s %s %s %s %s %s",
                    row[0],
                    row[1],
                    row[2],
                    peak_wind_gust,
                    peak_wind_drct,
                    peak_wind_time,
                )
                continue
            print(
                f"{row[0]} {row[1]} {peak_wind_gust} {peak_wind_drct} "
                f"{peak_wind_time}"
            )

            # LOG.info("%s %s -> %s", row[0], row[1], pwx)
            icursor2.execute(
                f"update t{now.year} SET peak_wind_gust = %s, "
                "peak_wind_drct = %s, peak_wind_time = %s WHERE station = %s "
                "and valid = %s",
                (
                    peak_wind_gust,
                    peak_wind_drct,
                    peak_wind_time,
                    row[1],
                    row[0],
                ),
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
