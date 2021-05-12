"""Plot squaw creek flows"""
from calendar import month_abbr

import numpy as np
import matplotlib.pyplot as plt
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("squaw")
    icursor = pgconn.cursor()

    (fig, ax) = plt.subplots(1, 1)

    for yr in range(1991, 2022):
        icursor.execute(
            """
            SELECT extract(doy from valid) as d, max(cfs) from real_flow
            WHERE extract(year from valid) = %s and cfs > 0
            GROUP by d ORDER by d ASC
            """
            % (yr,)
        )
        obs = np.ma.ones((366,), "f") * -1
        for row in icursor:
            obs[int(row[0]) - 1] = row[1]
        obs.mask = obs < 1

        if yr in [2021, 2012, 1993]:
            ax.plot(range(1, 367), obs, linewidth=2, label=yr, zorder=2)
        else:
            ax.plot(range(1, 367), obs, color="tan", zorder=1)

    ax.plot([1, 366], [3700, 3700], label="Flood")
    ax.legend(loc="best", ncol=5)
    ax.set_title("Ames Squaw Creek at Lincoln Way (1991-2021)")
    ax.set_ylabel("Water Flow [cfs], log scale")
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(month_abbr[1:])
    ax.set_xlim(0, 366)
    ax.set_yscale("log")
    ax.grid(True)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
