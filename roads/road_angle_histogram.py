"""Histogram of Road anagles"""

from __future__ import print_function

import math

import matplotlib.pyplot as plt
import numpy as np
import psycopg2
from shapely.wkb import loads


def makedir(u, v):
    if v == 0:
        v = 0.000000001
    dd = math.atan(u / v)
    ddir = (dd * 180.00) / math.pi

    if u > 0 and v > 0:  # First Quad
        ddir = 180 + ddir
    elif u > 0 and v < 0:  # Second Quad
        ddir = 360 + ddir
    elif u < 0 and v < 0:  # Third Quad
        ddir = ddir
    elif u < 0 and v > 0:  # Fourth Quad
        ddir = 180 + ddir

    return int(math.fabs(ddir))


def main():
    """Go"""
    pgconn = psycopg2.connect(database="postgis", host="iemdb", user="nobody")
    cursor = pgconn.cursor()

    cursor.execute("""SELECT geom from roads_base""")

    weights = []
    drcts = []
    for row in cursor:
        if row[0] is None:
            continue
        geom = loads(row[0].decode("hex"))
        for line in geom:
            (x, y) = line.xy
            for i in range(len(x) - 1):
                dist = ((x[i + 1] - x[i]) ** 2 + (y[i + 1] - y[i]) ** 2) ** 0.5
                weights.append(dist)
                drcts.append(makedir(x[i + 1] - x[i], y[i + 1] - y[i]))

    (fig, ax) = plt.subplots(1, 1)
    # Some tricks here
    hist, bin_edges = np.histogram(
        drcts, np.arange(-2.5, 363, 5), weights=weights, normed=True
    )
    # hist is 73, we only want 36
    hist2 = hist[:36] + hist[36:72]
    # double up first bin
    hist2[0] = hist2[0] + hist[72]

    ax.bar(bin_edges[:36], hist2, width=5, align="edge")
    ax.set_xlabel("Road Orientation")
    ax.set_xticks([0, 45, 90, 135])
    ax.set_xticklabels(["N-S", "NE_SW", "E-W", "NW-SE", "N-S"])
    ax.grid(True)
    ax.set_ylabel("Normalized Frequency")
    ax.set_title(
        (
            "Orientation of Primary Iowa Roadways\n"
            "(based on Interstates, US Highways, and some IA Highways)"
        )
    )

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
