"""Unsure."""

import matplotlib.pyplot as plt
import numpy as np
from pyiem.util import get_dbconn


def do(station):
    """do work."""
    tot_tmpf = np.zeros((12 * 60), "f")
    max_tmpf = np.zeros((12 * 60), "f")
    tot_sknt = np.zeros((12 * 60), "f")
    tot_cnt = np.zeros((12 * 60), "f")

    pgconn = get_dbconn("asos1min")
    acursor = pgconn.cursor()
    acursor2 = pgconn.cursor()
    acursor.execute(
        "select date from (select date(valid), min(tmpf), max(tmpf) from "
        "alldata_1minute where station = %s and "
        "extract(month from valid) in (3,4) and "
        "tmpf BETWEEN -30 and 60 and "
        "extract(hour from valid) between 0 and 6 GROUP by date) as foo "
        "where min <= 32 and max > 32",
        (station,),
    )

    for row in acursor:
        tmpf = np.zeros((12 * 60), "f")
        sknt = np.zeros((12 * 60), "f")
        cnt = np.zeros((12 * 60), "f")
        acursor2.execute(
            "SELECT valid + '3 hours'::interval, tmpf, sknt from "
            "t%s_1minute where station = '%s' and "
            "valid + '3 hours'::interval BETWEEN '%s 00:00' and '%s 11:59' "
            "and tmpf between 10 and 89 ORDER by valid ASC"
            % (
                row[0].year,
                station,
                row[0].strftime("%Y-%m-%d"),
                row[0].strftime("%Y-%m-%d"),
            )
        )
        for row2 in acursor2:
            pos = row2[0].hour * 60 + row2[0].minute
            tmpf[pos] = row2[1]
            sknt[pos] = row2[2]
            cnt[pos] = 1.0
            if row2[1] <= 32 and pos > 180:
                break
        if pos == 719 or np.min(tmpf[: (pos - 1)]) < 32 or row2[2] > 4:
            continue
        pos += 1
        tot_tmpf[-pos:] += tmpf[:pos]
        max_tmpf[-pos:] = np.where(
            tmpf[:pos] > max_tmpf[-pos:], tmpf[:pos], max_tmpf[-pos:]
        )
        tot_sknt[-pos:] += sknt[:pos]
        tot_cnt[-pos:] += cnt[:pos]

    return max_tmpf, tot_tmpf, tot_sknt, tot_cnt


def main():
    """GO Main Go."""
    fig = plt.figure()
    ax = fig.add_subplot(111)

    max_tmpf, tot_tmpf, tot_sknt, tot_cnt = do("DSM")
    ax.plot(
        np.arange(720),
        tot_tmpf / tot_cnt,
        color="r",
        label="Des Moines %.0f events" % (tot_cnt[-1],),
    )
    # ax.plot( numpy.arange(720), max_tmpf, color='pink')
    # ax.plot( [0,720], [32,32], color='k')
    ax.set_ylabel(r"Mean Temperature $^{\circ}\mathrm{F}$")
    ax.set_title(
        "March/April Radiational Cooling Events [2001-2011]\n"
        r"temp reaches 32$^{\circ}\mathrm{F}$ between 3-6 AM "
        "with winds below 5 knots"
    )
    ax.set_xlabel(r"Time before observation of 32$^{\circ}\mathrm{F}$")
    max_tmpf, tot_tmpf, tot_sknt, tot_cnt = do("ALO")
    ax.plot(
        np.arange(720),
        tot_tmpf / tot_cnt,
        color="b",
        label="Waterloo %.0f events" % (tot_cnt[-1],),
    )
    # ax.plot( numpy.arange(720), max_tmpf, color='skyblue')
    ax.set_xlim(540, 720)
    ax.set_xticks(np.arange(540, 721, 30))
    ax.set_xticklabels(
        ["-3hr", "-150min", "-2hr", "-90min", "-1hr", "-30min", "0"]
    )
    ax.grid(True)
    ax.set_ylim(30, 40)
    ax.legend()

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
