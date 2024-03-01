"""A one-off feature plot."""

import datetime

import numpy as np

import matplotlib.colors as mpcolors
from pyiem.plot import james
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main."""
    SQUAW = get_dbconn("squaw")
    cursor = SQUAW.cursor()

    data = np.ma.ones((datetime.date.today().year - 1990 + 1, 53), "f") * -99.0
    data.mask = np.where(data < 0, True, False)
    cursor.execute(
        """
      SELECT extract(year from valid)::int as yr,
      extract(week from valid)::int as week,
      avg(cfs) from real_flow GROUP by yr, week
    """
    )

    for row in cursor:
        data[row[0] - 1990, row[1] - 1] = row[2]

    levels = np.percentile(
        np.where(data < 0, 0, data), [10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
    )
    norm = mpcolors.BoundaryNorm(levels, 12)

    cmap = james()
    cmap.set_under("#FFFFFF")
    (fig, ax) = plt.subplots(1, 1)
    res = ax.imshow(
        np.flipud(data),
        interpolation="nearest",
        extent=(1, 54, 1989.5, 2021.5),
        cmap=cmap,
        norm=norm,
        aspect="auto",
    )
    ax.set_xticks(np.arange(1, 56, 7))
    ax.set_xlim(1, 53)
    ax.set_xticklabels(
        (
            "Jan 1",
            "Feb 19",
            "Apr 8",
            "May 27",
            "Jul 15",
            "Sep 2",
            "Oct 21",
            "Dec 9",
        )
    )
    ax.grid()
    ax.set_title(
        "Squaw Creek @ Lincoln Way in Ames\nWeekly Average Streamflow"
    )
    ax.set_ylabel("Year")
    ax.set_xlabel("Day of Year")
    fig.colorbar(res, extend="both", label="Cubic Feet per Second")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
