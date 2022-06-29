"""Generate a plot of the equation shown in the ASOS manual for the website"""
from pyiem.plot.use_agg import plt
import numpy as np


def main():
    """Go Main Go."""
    x = np.arange(0, 4, 0.01)
    y = np.round(x + 0.6 * x**2, 2)

    (fig, ax) = plt.subplots(1, 1)

    ax.bar(
        x - 0.005,
        y,
        label="C=A(1 + 0.60A)",
        fc="r",
        ec="r",
        zorder=1,
        width=0.01,
    )
    ax.bar(x - 0.005, x, label="C=A", fc="b", ec="b", zorder=2, width=0.01)
    ax.bar(
        x - 0.005,
        y - x,
        label="Difference",
        zorder=3,
        fc="g",
        ec="g",
        width=0.01,
    )
    ax.set_xlabel("(A) One Minute Heated Tipping Bucket Accumulation [inch]")
    ax.set_ylabel("(C) One Minute Reported Accumulation [inch]")
    ax.legend(loc=2)
    ax.set_xticks(np.arange(0, 0.51, 0.05))
    ax.set_yticks(np.arange(0, 1.01, 0.05))
    ax.set_xlim(0, 0.2)
    ax.set_ylim(0, 0.85)
    ax.set_title(
        (
            "ASOS Manual Eqn 3.4.2 Precipitation Adjustment\n"
            "Values are rounded after adjustment"
        )
    )

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
