"""Convert the plot.out into something more usable."""

import calendar

from pyiem.plot import figure


def main():
    """Go Main Go."""
    colnames = []
    gmd_p_idx = 0
    days = []
    gmd_p = []

    fig = figure(title="GMD by Day of the Year", logo="dep")
    ax1 = fig.add_axes((0.1, 0.1, 0.8, 0.8))
    # ax2 = fig.add_axes((0.1, 0.1, 0.8, 0.3))

    year = 1
    with open("plot.out", "r") as plot_file:
        for linenum, line in enumerate(plot_file):
            if linenum == 0:
                colnames = [s.strip() for s in line.strip().split("|")]
                gmd_p_idx = colnames.index("gmd_p")
                continue
            vals = line.strip().split()
            if len(vals) > 10:
                doy = int(vals[1])
                if doy == 1 and len(days) > 0:
                    ax1.plot(days, gmd_p, label=f"{year}")
                    days = []
                    gmd_p = []
                    year += 1
                days.append(int(vals[1]))
                gmd_p.append(float(vals[gmd_p_idx]))

    ax1.set_ylabel("GMD_P (mm?)")
    ax1.set_xlabel("Day of the Year")
    ax1.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax1.set_xticklabels(calendar.month_abbr[1:])
    ax1.legend(ncol=2, fontsize=8)
    ax1.grid(True)
    ax1.set_xlim(121, 244)
    ax1.set_ylim(0.1, 20)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
