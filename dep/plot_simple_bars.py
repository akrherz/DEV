"""Simple plot of data."""

from pyiem.plot.use_agg import plt

DATA = [-49, -41, -32, -21, -12, 0, 9, 21, 33, 46, 58]


def main():
    """Go Main Go."""
    (fig, ax) = plt.subplots(1, 1)
    ax.bar(range(len(DATA)), DATA)
    for i, val in enumerate(DATA):
        delta = -3 if val < 0 else 3
        ax.text(i, val + delta, "%i%%" % (val,), ha="center", va="center")
    ax.grid(True)
    ax.set_xticks(range(len(DATA)))
    ax.set_title(
        (
            "Iowa DEP Future Precipitation Scenarios\n"
            "Change in Hill Slope Soil Delivery by Linear "
            "Precipitation Adjustment"
        )
    )
    ax.set_xlabel('Precipitation Total Adjustment (baseline: 38.17")')
    ax.set_ylabel("Change in Soil Delivery (baseline: 3.5 T/a)")
    ax.set_xticklabels(
        [
            "-20%",
            "-16%",
            "-12%",
            "-8%",
            "-4%",
            "Base",
            "4%",
            "8%",
            "12%",
            "16%",
            "20%",
        ]
    )
    ax.grid(False)
    ax.set_ylim(-70, 70)
    ax.axhline(0, color="k")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
