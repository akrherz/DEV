"""An old plot."""

import calendar
import datetime
import os
import subprocess

import matplotlib.colors as mpcolors
import matplotlib.pyplot as plt
import numpy as np
import osgeo.gdal as gdal
from pyiem import reference
from pyiem.util import get_dbconn


def lalo2pt(lon, lat):
    """Simple."""
    x = int((-126.0 - lon) / -0.01)
    y = int((50.0 - lat) / 0.01)
    return x, y


def get_nexrad(date):
    """Get a timeseries of NEXRAD for a given date"""
    # loop between 12 and 20 UTC
    sts = datetime.datetime(date.year, date.month, date.day, 12, 0)
    ets = sts.replace(hour=20)
    now = sts
    interval = datetime.timedelta(minutes=15)
    res = [False] * (4 * 8)
    x1, y1 = lalo2pt(reference.IA_WEST, reference.IA_SOUTH)
    x2, y2 = lalo2pt(reference.IA_EAST, reference.IA_NORTH)

    sz = (y1 - y2) * (x2 - x1)
    i = 0
    while now < ets:
        fn = now.strftime(
            ("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png")
        )
        if not os.path.isfile(fn):
            now += interval
            i += 1
            continue
        n0r = gdal.Open(fn, 0)
        n0rd = n0r.ReadAsArray()
        data = n0rd[y2:y1, x1:x2]
        dbz = (data - 7.0) * 5.0
        coverage = np.sum(np.where(dbz >= 10, 1, 0)) / float(sz) * 100.0
        res[i] = coverage > 5
        now += interval
        i += 1

    return res


def find_events():
    """Do as I say."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        """WITH obs as (
      SELECT distinct date(issue) as dt, eventid, phenomena, significance, wfo
      from warnings where substr(ugc, 1, 3) = 'IAC'
      and phenomena in ('SV', 'TO')
      and significance = 'W' and extract(hour from issue at time zone 'UTC')
      between 20 and 24 and issue > '1996-01-01')

    SELECT dt, count(*) from obs GROUP by dt ORDER by dt ASC
    """
    )
    res = []
    for row in cursor:
        if row[1] > 4:
            res.append(row[0])
    return res


def fetch(event):
    """Get data."""
    mydir = event.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp")
    # likely already done
    if os.path.isdir(mydir):
        return
    os.makedirs(mydir)
    subprocess.call(
        ("rsync -ae ssh mesonet@mesonet:%s/n0r_*1???.png %s/")
        % (mydir, mydir),
        shell=True,
    )


def run():
    """Go run go."""
    if os.path.isfile("hits.npy"):
        hits = np.loadtxt("hits.npy")
        dry = np.loadtxt("dry.npy")
        total = np.loadtxt("total.npy")
    else:
        hits = np.zeros((32, 12))
        total = np.zeros(12)
        dry = np.zeros(12)
        events = find_events()
        for event in events:
            fetch(event)
            res = get_nexrad(event)
            woy = event.month - 1
            # woy = event.isocalendar()[1] - 1
            hits[:, woy] += np.where(res, 1, 0)
            if True not in res:
                dry[woy] += 1
            total[woy] += 1

        for i in range(12):
            if total[i] > 0:
                hits[:, i] = hits[:, i] / float(total[i]) * 100.0
            else:
                hits[:, i] = -1
        np.savetxt("hits.npy", hits)
        np.savetxt("dry.npy", dry)
        np.savetxt("total.npy", total)

    (fig, ax) = plt.subplots()
    cmap = plt.get_cmap("YlGnBu")
    cmap.set_under("#EEEEEE")
    cmap.set_bad("white")
    norm = mpcolors.BoundaryNorm(np.arange(0, 101, 5), cmap.N)
    mp = ax.imshow(
        hits,
        extent=[0.5, 12.5, 11.875, 19.875],
        interpolation="nearest",
        aspect="auto",
        cmap=cmap,
        norm=norm,
    )
    fig.colorbar(mp, label="Frequency [%]", extend="min")
    ax.grid()
    ax.set_xticks(np.arange(1, 13))
    xlabels = calendar.month_abbr[1:]
    for i, (d, t) in enumerate(zip(dry, total, strict=False)):
        if t > 0:
            xlabels[i] += "\n%.0f\n%.0f%%" % (t, d / float(t) * 100.0)
    ax.set_xticklabels(xlabels)
    ax.set_title(
        (
            "7 AM - 3 PM Iowa RADAR (5% area >= 10 dBz) Coverage\n"
            "On Days with 5+ Iowa Severe Warnings between 3PM - 7PM"
        )
    )
    ax.set_yticks(np.arange(12, 20))
    ax.set_yticklabels(
        ["7 AM", "8 AM", "9 AM", "10 AM", "11 AM", "Noon", "1 PM", "2 PM"]
    )
    ax.set_ylabel("Times are always Central Daylight Time")
    ax.set_xlabel("Partitioned by month, %.0f total days" % (np.sum(total),))
    ax.text(
        0,
        -0.06,
        "Events\nNo 'Storms'",
        transform=ax.transAxes,
        ha="right",
        va="top",
    )
    ax.set_position([0.15, 0.15, 0.6, 0.75])
    fig.savefig("test.png")


if __name__ == "__main__":
    run()
