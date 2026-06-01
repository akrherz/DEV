"""Convert the plot.out into something more usable."""

import calendar
import sys

from dailyerosion.reference import KG_M2_TO_TON_ACRE
from pyiem.plot import figure


def main():
    """Go Main Go."""
    colnames = []
    gmd_p_idx = 0
    days = []
    gmd_p = []

    fig = figure(
        title="WEPS Wind Erosion by Date for 070102020203_514", logo="dep"
    )
    ax1 = fig.add_axes((0.1, 0.1, 0.8, 0.8))
    # ax2 = fig.add_axes((0.1, 0.1, 0.8, 0.3))

    year = 2007
    total = 0
    with open(sys.argv[1], "r") as plot_file:
        for linenum, line in enumerate(plot_file):
            if linenum == 0:
                colnames = [s.strip() for s in line.strip().split("|")]
                gmd_p_idx = colnames.index("tot_loss")
                continue
            vals = line.strip().split()
            if len(vals) > 10:
                doy = int(vals[1])
                if doy == 1 and len(days) > 0:
                    ax1.scatter(
                        days, gmd_p, label=f"{year} {total:.1f} T/a", s=50
                    )
                    days = []
                    gmd_p = []
                    year += 1
                    total = 0
                days.append(int(vals[1]))
                ta = float(vals[gmd_p_idx]) * KG_M2_TO_TON_ACRE * -1
                total += ta
                gmd_p.append(ta)

    ax1.set_ylabel("Total Loss (ton/acre)")
    ax1.set_xlabel("Day of the Year")
    ax1.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax1.set_xticklabels(calendar.month_abbr[1:])
    ax1.legend(ncol=2, fontsize=8)
    ax1.grid(True)
    ax1.set_xlim(0, 366)
    # ax1.set_ylim(0.1, 20)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
