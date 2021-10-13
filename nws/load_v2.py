"""Warning load by minute"""

import pytz
from pyiem.util import get_dbconn
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

TZ = pytz.timezone("America/Chicago")
PGCONN = get_dbconn("postgis")


def getp():
    """Do Query"""
    cursor = PGCONN.cursor()
    cursor.execute(
        """
     WITH data as
     (select distinct hvtec_nwsli,
     generate_series(issue, expire, '1 minute'::interval) as t
     from warnings_2019 where phenomena = 'FL' and significance = 'W'
     and substr(ugc, 1, 2) = 'NE' and issue > '2019-03-01'),
     agg as (
         select t, count(*) from data GROUP by t
     ),
     ts as (select generate_series('2019-03-01',
     '2020-01-01', '1 minute'::interval) as t)

     SELECT ts.t, a.count from ts LEFT JOIN agg a on (ts.t = a.t)
     ORDER by ts.t ASC
    """
    )
    times = []
    counts = []
    for row in cursor:
        times.append(row[0])
        counts.append(row[1] if row[1] is not None else 0)

    return times, counts


def main():
    """Main"""
    b_t, b_c = getp()

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    ax.fill_between(b_t, 0, b_c, zorder=1, color="teal")
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1], tz=TZ))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b", tz=TZ))

    ax.set_title("2019 Nebraska Active Flood Warnings")
    ax.set_ylabel("Active Warning Count")
    ax.set_ylim(bottom=0.1)
    ax.set_xlim(b_t[0], b_t[-1])
    first = None
    last = None
    for t, c in zip(b_t, b_c):
        if c > 0 and first is None:
            first = t
        if c == 0 and first is not None and last is None:
            last = t

    fmt = "%d %b %Y %-I:%M %p"
    ax.set_xlabel(
        "Active Streak Duration %s - %s"
        % (first.strftime(fmt), last.strftime(fmt))
    )
    # fig.text(0.01, 0.01, "@akrherz, generated 19 Dec 2019")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
