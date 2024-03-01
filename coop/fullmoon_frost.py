"""First frost and moon phase."""

import datetime

import ephem
import numpy as np

import matplotlib.pyplot as plt
from pyiem.util import get_dbconn


def s2dt(s):
    """Convert ephem string to datetime instance"""
    return datetime.datetime.strptime(str(s), "%Y/%m/%d %H:%M:%S")


def run(cursor, myloc):
    """Get the first fall sub 29 and when the nearest full moon was
    that year"""
    cursor.execute(
        "SELECT year, min(day), min(extract(doy from day)) from "
        "alldata_ia where station = 'IATAME' and low < 32 and month > 6 "
        "GROUP by year ORDER by year ASC"
    )
    juliandays = []
    moondiff = []
    for row in cursor:
        juliandays.append(row[2])
        myloc.date = f"{row[1]:%Y/%m/%d}"

        lastd = s2dt(ephem.previous_full_moon(myloc.date)).date()
        today = row[1]
        nextd = s2dt(ephem.next_full_moon(myloc.date)).date()
        forward = (nextd - today).days
        backward = (today - lastd).days
        if backward == forward:
            moondiff.append(backward)
        elif backward < forward:
            moondiff.append(backward)
        elif forward < backward:
            moondiff.append(0 - forward)

    return moondiff, juliandays


def main():
    """Go Main Go."""
    COOP = get_dbconn("coop")
    cursor = COOP.cursor()

    # moon = ephem.Moon()
    myloc = ephem.Observer()
    myloc.lat = "41.99206"
    myloc.long = "-93.62183"

    moondiff, juliandays = run(cursor, myloc)
    juliandays = np.array(juliandays)

    (fig, ax) = plt.subplots(1, 1)
    ax.scatter(moondiff, juliandays, marker="x", s=40)
    ax.set_title(r"1893-2021 Ames First Fall sub 32$^\circ$F Temperature")
    ax.set_ylabel("Date")
    ax.set_xlabel("Days to nearest Full Moon")
    ax.set_xlim(-16, 16)
    ax.axhline(np.average(juliandays), linestyle="-.", lw=2, color="r")
    ax.set_yticks((258, 265, 274, 281, 288, 295, 305, 312, 319))
    ax.set_yticklabels(
        (
            "Sep 15",
            "Sep 22",
            "Oct 1",
            "Oct 8",
            "Oct 15",
            "Oct 22",
            "Nov 1",
            "Nov 8",
            "Nov 15",
        )
    )

    ax.grid(True)
    fig.savefig("220916.png")


if __name__ == "__main__":
    main()
