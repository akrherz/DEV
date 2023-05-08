"""Shrug."""
import calendar

import matplotlib.pyplot as plt
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    CONN = get_dbconn("coop")
    cursor = CONN.cursor()

    data = []
    for _ in range(12):
        data.append([])

    cursor.execute(
        "SELECT month, high - low from alldata_ia where station = 'IA0200'"
    )
    for row in cursor:
        data[row[0] - 1].append(row[1])

    (fig, ax) = plt.subplots(1, 1)

    ax.boxplot(data)
    ax.set_ylabel(r"Daily High & Low Temp Diff $^\circ$F")
    ax.set_ylim(bottom=0)
    ax.grid(True)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_title("1893-2013 Ames Daily Hi-Lo Temp Difference")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
