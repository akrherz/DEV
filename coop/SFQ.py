"""exploritory look at 6 hourly snowfall."""

import datetime
from collections import OrderedDict

import pytz
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    HADS = get_dbconn("hads")
    cursor = HADS.cursor()

    STATIONS = OrderedDict(
        [
            ("BSPM2", "Baltimore BWI\n"),
            ("IAD", "Washington DC\nDulles"),
            ("JKL", "Jackson TN\nNWS WFO"),
            ("KCIV2", "Sterling VA\n"),
            ("DCA", "Washington DC\nReagan"),
        ]
    )

    (fig, ax) = plt.subplots(1, 1)
    y = 0 - len(STATIONS)
    ax.set_ylim(y, 0)

    EASTERN = pytz.timezone("America/New_York")
    x0 = datetime.datetime.now()
    x0 = x0.replace(tzinfo=EASTERN)
    x0 = x0.replace(day=22, hour=1, minute=0, second=0, microsecond=0)
    x1 = x0 + datetime.timedelta(hours=48)

    xticks = []
    xticklabels = []
    now = x0
    while now <= x1:
        xticks.append(now)
        fmt = "%-I %p" if now.hour > 1 else "1 AM\n%-d %b"
        xticklabels.append(now.strftime(fmt))
        now += datetime.timedelta(hours=6)

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.grid(True)
    ax.set_yticks(range(y, 0))
    ax.set_yticklabels(["%s [%s]" % (STATIONS[k], k) for k in STATIONS])

    for _, station in enumerate(STATIONS):
        cursor.execute(
            """
            SELECT valid, min(value) from raw2016_01 where station = %s
            and valid >= %s and value > 0 and
            substr(key, 1, 3) = 'SFQ' GROUP by valid ORDER by valid
        """,
            (station, x0),
        )
        total = 0
        for row in cursor:
            ts = row[0].astimezone(EASTERN)
            if station == "BSPM2" and row[0].hour % 6 != 0:
                continue
            ax.text(
                ts - datetime.timedelta(hours=3),
                y,
                "%.1f" % (row[1],) if row[1] > 0.05 else "T",
                ha="center",
                va="center",
            )
            total += row[1]
        ax.text(
            x1 + datetime.timedelta(hours=5),
            y,
            f"{total:.1f}",
            ha="right",
            va="center",
        )
        y += 1

    ax.set_xlim(xticks[0], xticks[-1])
    box = ax.get_position()
    ax.set_position([0.2, box.y0 + 0.05, 0.7, box.height - 0.05])
    ax.set_ylim(0 - len(STATIONS) - 0.5, -0.5)
    ax.set_xlabel("Eastern Standard Time")
    ax.set_title("6 Hour Interval Snowfall Reports\nbased on SFQ SHEF Reports")

    fig.savefig("160125.png")


if __name__ == "__main__":
    main()
