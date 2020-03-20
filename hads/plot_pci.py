"""plot precip accumulator"""
from __future__ import print_function

import matplotlib.pyplot as plt
from pyiem.util import get_dbconn


def main():
    """Plot"""
    pgconn = get_dbconn("hads")
    cursor = pgconn.cursor()
    cursor.execute(
        """SELECT valid, value from raw2017_08 where
    station = 'CFMT2' and valid > '2017-08-25' and key = 'PCIRZZ'
    ORDER by valid ASC"""
    )
    times = []
    accum = []
    for row in cursor:
        times.append(row[0])
        accum.append(row[1])
    print(accum)
    (fig, ax) = plt.subplots(1, 1)
    ax.plot(times, accum)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
