"""Jump up in feels like temp."""

import pandas as pd
from pyiem.database import get_dbconn
from pyiem.plot import figure


def main():
    """Go Main Go."""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        select date(valid), max(feel) from alldata where
        station = 'AMW' and tmpf >= 80 and feel > tmpf
        GROUP by date ORDER by date ASC"""
    )
    year = 0
    maxval = 80
    maxjump = 0
    res = []
    entry = {}
    firstvals = []
    for row in cursor:
        if row[0].year == 2022:
            print(entry, maxjump, maxval)
        if row[0].year != year:
            if entry:
                res.append(entry)
            entry = {}
            year = row[0].year
            maxval = 80
            maxjump = 0
        if row[1] > maxval:
            if maxval == 80:
                firstvals.append(row[1])
            jump = row[1] - maxval
            maxval = row[1]
            if jump > maxjump:
                entry = {"year": row[0].year, "jump": jump, "max": maxval}
                maxjump = jump
                print("%s %s %s" % (row[0], row[1], jump))
    res.append(entry)
    df = pd.DataFrame(res)
    fig = figure(
        title="Ames :: Maximum One Day Year-to-date Increase in Heat Index",
        subtitle=(
            "Based on ASOS hourly data and including only additive heat index"
            ", assuming 80F starting point."
        ),
        apctx={"_r": "43"},
    )
    ax = fig.add_axes([0.1, 0.65, 0.85, 0.25])
    ax.bar(df["year"], df["jump"], color="r")
    ax.set_ylim(0, 17)
    ax.set_yticks(range(0, 17, 4))
    ax.set_ylabel("Max Daily Increase (F)")
    ax.grid(True)
    ax.set_xlim(1996.5, 2022.5)

    ax = fig.add_axes([0.1, 0.36, 0.85, 0.24])
    ax.bar(df["year"], df["jump"], bottom=(df["max"] - df["jump"]), color="r")
    ax.set_ylabel("Actual Max Jump (F)")
    ax.grid(True)
    ax.set_xlim(1996.5, 2022.5)

    ax = fig.add_axes([0.1, 0.08, 0.85, 0.24])
    ax.bar(df["year"], firstvals, color="r")
    ax.set_xlim(1996.5, 2022.5)
    ax.set_ylim(80, 100)
    ax.grid(True)
    ax.set_ylabel("First Day Max (F)")
    ax.set_xlabel("*2022 through 9 May")

    fig.savefig("220510.png")


if __name__ == "__main__":
    main()
