"""Plot peaks."""

import matplotlib.pyplot as plt
import numpy as np
import pytz
from numpy.lib import stride_tricks
from pyiem.database import get_dbconn
from pyiem.util import utc


def main():
    """Go Main Go."""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()

    basets = utc(1999, 1, 1)

    data = np.zeros((17 * 365 * 24 * 60), "f")
    #
    cursor.execute(
        """SELECT valid at time zone 'UTC', precip from alldata_1minute
        WHERE station = 'MCW' and precip > 0"""
    )
    for row in cursor:
        ts = row[0].replace(tzinfo=pytz.timezone("UTC"))
        delta = ts - basets
        offset = int(delta.days * 1440 + delta.seconds / 60.0)
        if row[1] > 0.35:
            continue
        data[offset] = row[1]

    def rolling(a, window):
        shape = (a.size - window + 1, window)
        strides = (a.itemsize, a.itemsize)
        return stride_tricks.as_strided(a, shape=shape, strides=strides)

    x = range(1, 3 * 60 + 1)
    y = []
    for i in x:
        Z = rolling(data, i)
        sums = np.sum(Z, 1)
        y.append(np.max(sums))

    np.savetxt("mcw.npyb", y)
    xcid = range(1, 3 * 60 + 1)
    ycid = np.loadtxt("cid.npyb")
    xalo = range(1, 3 * 60 + 1)
    yalo = np.loadtxt("alo.npyb")
    xsux = range(1, 3 * 60 + 1)
    ysux = np.loadtxt("sux.npyb")
    xmcw = range(1, 3 * 60 + 1)
    ymcw = np.loadtxt("mcw.npyb")
    xdsm = range(1, 6 * 60 + 1)
    ydsm = np.loadtxt("dsm.npyb")

    (fig, ax) = plt.subplots(1, 1)

    ax.plot(xdsm, ydsm, label="Des Moines", lw=2)
    ax.plot(xcid, ycid, label="Cedar Rapids", lw=2)
    ax.plot(xalo, yalo, label="Waterloo", lw=2)
    ax.plot(xsux, ysux, label="Sioux City", lw=2)
    ax.plot(xmcw, ymcw, label="Mason City", lw=2)
    ax.set_xlim(0, 180)
    ax.legend(loc=4, ncol=2)
    ax.set_xticks(range(0, 181, 15))
    ax.grid(True)
    ax.set_title(
        "2000-2015 Iowa Airport ASOS 1 Minute Precip\n"
        "Peak Accumulations over Window of Time"
    )
    ax.set_xlabel("Time Window in Minutes")
    ax.set_ylabel("Largest Accumulation [inch]")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
