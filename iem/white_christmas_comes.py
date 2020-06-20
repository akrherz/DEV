"""When does White Christmas Apear?"""
import datetime

import numpy as np
from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt


def main():
    """Go Main Go."""
    pgconn = get_dbconn("coop")
    ccursor = pgconn.cursor()
    ccursor2 = pgconn.cursor()

    # Get white christmases
    ccursor.execute(
        "SELECT year from alldata_ia where sday = '1225' and "
        "snowd >= 1 and station = 'IA2203' and year > 1894"
    )

    counts = np.zeros((60,), "f")

    for row in ccursor:
        ccursor2.execute(
            "SELECT day, snowd from alldata_ia where station = 'IA2203' and "
            "sday < '1225' and year = %s and snowd is not null "
            "ORDER by day DESC LIMIT 60",
            (row[0],),
        )
        idx = -2
        counts[-1] += 1
        for row2 in ccursor2:
            if row2[1] >= 1:
                counts[idx] += 1
                idx -= 1
            else:
                break

    ets = datetime.date(2000, 12, 25)
    sts = ets - datetime.timedelta(days=60)
    xticks = []
    xticklabels = []
    for i in range(2, 60, 3):
        ts = sts + datetime.timedelta(days=i + 1)
        xticks.append(i)

        xticklabels.append(ts.strftime("%-d\n%b"))

    (fig, ax) = plt.subplots(1, 1)

    ax.bar(
        np.arange(60),
        counts / counts[-1] * 100.0,
        width=1,
        align="center",
        fc="b",
        ec="b",
        label="Snowcover on 12/25 Arrival",
    )
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(28, 60)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.grid(True)
    ax.set_ylabel("Frequency [%]")
    ax.set_title(
        "Des Moines 1895-2018 White Christmas\nDate which snow cover "
        "(1+ inch) arrived"
    )
    ax.legend(loc=2)

    fig.savefig("191218.png")


if __name__ == "__main__":
    main()
