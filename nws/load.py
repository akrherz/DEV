"""Warning load by minute"""
import datetime

import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pyiem.util import get_dbconn

TZ = pytz.timezone("America/Chicago")
PGCONN = get_dbconn("postgis")


def getp(phenomena, sts, ets):
    """Do Query"""
    cursor = PGCONN.cursor()
    table = "sbw_%s" % (sts.year,)
    print("%s %s %s" % (table, sts, ets))
    cursor.execute(
        """
     WITH data as
     (SELECT t, count(*) from
     (select phenomena,
     generate_series(issue, expire, '1 minute'::interval) as t
     from """
        + table
        + """ where status = 'NEW' and issue > %s and
     issue < %s and phenomena in %s) as foo
     GROUP by t),

     ts as (select generate_series(%s,
      %s, '1 minute'::interval) as t)

     SELECT ts.t, data.count from ts LEFT JOIN data on (data.t = ts.t)
     ORDER by ts.t ASC
    """,
        (sts, ets, phenomena, sts, ets),
    )
    times = []
    counts = []
    for row in cursor:
        times.append(row[0])
        counts.append(row[1] if row[1] is not None else 0)

    return times, counts


def main(date):
    """Main"""
    sts = date - datetime.timedelta(hours=24)
    ets = date + datetime.timedelta(hours=24)
    to_t, to_c = getp(("TO",), sts, ets)
    b_t, b_c = getp(("SV", "TO"), sts, ets)

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    ax.fill_between(
        b_t, 0, b_c, zorder=1, color="teal", label="Severe TStorm + Tornado"
    )
    ax.fill_between(to_t, 0, to_c, zorder=2, color="r", label="Tornado")

    ax.grid(True)
    ax.xaxis.set_major_locator(
        mdates.HourLocator(byhour=[0, 6, 12, 18], tz=TZ)
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%I %p\n%d %b", tz=TZ))

    ax.set_title(
        ("%s National Weather Service " "Storm Based Warning Load")
        % (date.strftime("%-d %b %Y"),)
    )
    ax.set_ylabel("Active Warning Count")
    ax.legend(loc="best", ncol=2)
    ax.set_ylim(bottom=0.1)
    ax.set_xlim(to_t[0], to_t[-1])
    ax.set_xlabel("Central Daylight Time")
    fig.text(0.01, 0.01, "@akrherz, generated 27 Apr 2017")

    fig.savefig("%s.png" % (date.strftime("%Y%m%d"),))
    plt.close()


def work():
    """Our workflow"""
    events = (
        "4/27/11, 3/2/11, 4/26/11, 5/25/11, 10/26/10, 4/15/11, 1/10/08,"
        " 4/10/09, 6/11/09, 5/11/08, 5/22/11, 6/2/09, 7/22/08, 7/1/12, "
        "8/5/10, 6/9/11, 6/21/11, 5/26/11, 4/26/11, 8/2/08"
    )
    for event in events.split(","):
        print(event)
        date = datetime.datetime.strptime(event.strip(), "%m/%d/%y")
        date = date.replace(hour=12, tzinfo=pytz.utc)
        main(date)


if __name__ == "__main__":
    work()
