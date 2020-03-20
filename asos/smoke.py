"""Reporting Smoke."""
from __future__ import print_function

import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pyiem.util import get_dbconn


def main():
    """Go"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    cursor.execute(
        """
    with data as (
        select distinct t.iemid,
        date_trunc('hour', valid + '10 minutes'::interval) as v from
        current_log c JOIN stations t on (c.iemid = t.iemid)
        where raw ~* ' FU ' and t.country = 'US')
    SELECT v, count(*) from data GROUP by v ORDER by v ASC
    """
    )
    xs = []
    ys = []
    for row in cursor:
        xs.append(row[0])
        ys.append(row[1])

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(xs, ys, width=(1.0 / 24.0))
    ax.grid(True)
    ax.set_ylabel("Number of ASOS/METAR Sites")
    ax.set_xlabel("3-5 July 2017 Valid Time (Central Daylight Time)")
    ax.set_title(
        (
            "Number of ASOS/METAR Sites Reporting Smoke (FU)\n"
            "based on METAR reports for the United States processed by IEM"
        )
    )
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter(
            "%-I %p\n%-d %b", tz=pytz.timezone("America/Chicago")
        )
    )
    ax.set_position([0.1, 0.15, 0.8, 0.75])
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
