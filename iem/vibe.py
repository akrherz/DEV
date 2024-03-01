"""Plot my car's mileage"""

import calendar
import datetime

import numpy as np

import matplotlib.pyplot as plt


def main():
    """Go"""
    climo = [
        18.5,
        24.8035714285714,
        37.0483870967742,
        49.8,
        61.258064516129,
        70.4,
        73.741935483871,
        71.4516129032258,
        64.2,
        52.1935483870968,
        36.2666666666667,
        23.0483870967742,
    ]

    x = []
    y = []
    months = []
    for _i in range(12):
        months.append([])
    for line in open("vibe.csv"):
        tokens = line.split(",")
        ts = datetime.datetime.strptime(tokens[0], "%m/%d/%Y")
        x.append(int(ts.strftime("%j")))
        pos = -1
        if tokens[-1].strip() == "":
            pos = -2
        y.append(float(tokens[pos]))

        months[int(ts.month) - 1].append(float(tokens[pos]))

    (fig, ax) = plt.subplots(1, 1)

    ax.boxplot(months)
    ax.set_ylabel("Miles Per Gallon")
    ax.set_title(
        (
            "IEM1 (2005 then 2008 Pontiac Vibe) Gas Mileage + "
            "Avg Air Temp\n4 March 2005 to 9 Oct 2017 (165,000 miles)"
        )
    )
    ax.plot([0, 13], [np.average(y), np.average(y)], lw=2.5, color="green")
    ax.text(
        0.5,
        np.average(y),
        "%.1f\nAvg" % (np.average(y),),
        color="green",
        ha="right",
        va="center",
        bbox=dict(color="white"),
    )
    y2 = ax.twinx()
    y2.plot(range(1, 13), climo, color="purple", lw=2)
    y2.set_ylabel(r"Average Monthly Temperature $^\circ$F", color="purple")
    y2.set_ylim(-10, 90)
    ax.set_ylim(22, 38)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0.5, 12.5)
    ax.grid(True)
    y2.set_yticks(
        np.linspace(
            y2.get_yticks()[0], y2.get_yticks()[-1], len(ax.get_yticks())
        )
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
