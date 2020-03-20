"""Plot number of watches per day for a given month"""

import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt
import numpy as np
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis")
    years = np.arange(1997, 2019)
    days = np.arange(1, 32)
    data = np.ma.zeros((len(years), len(days)))
    data[-1, -10:] = -1
    cursor = pgconn.cursor()
    cursor.execute(
        """
    SELECT extract(year from issued) as year,
    extract(day from issued) as day, count(*) from
    watches where type = 'TOR' and extract(month from issued) = 5
    GROUP by year, day
    """
    )
    for row in cursor:
        data[int(row[0]) - 1997, int(row[1]) - 1] = row[2]
    data.mask = data < 0
    print(data)
    ax = plt.axes([0.1, 0.15, 0.9, 0.75])
    cmap = plt.get_cmap("plasma")
    cmap.set_under("white")
    cmap.set_bad("gray")
    res = ax.imshow(
        np.flipud(data),
        cmap=cmap,
        extent=[0.5, 31.5, 1996.5, 2018.5],
        vmin=1,
        aspect="auto",
        zorder=4,
        alpha=0.8,
    )
    plt.colorbar(res, label="count")
    ax.set_yticks(range(1998, 2019, 2))
    ax.grid(True, zorder=3)
    ax.set_title(
        "1997-2018 May\nStorm Prediction Center Daily Tornado Watch Count"
    )
    ax.set_xlabel("CDT Calendar Day of May")
    plt.gcf().text(0.01, 0.01, "@akrherz, generated 22 May 2018")
    plt.gcf().savefig("test.png")


if __name__ == "__main__":
    main()
