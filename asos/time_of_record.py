""" Attempt to compute the time of a record high temperature! """
from calendar import month_abbr

from pyiem.util import get_dbconn
import matplotlib.pyplot as plt


def main():
    """Go Main Go."""
    COOP = get_dbconn("coop")
    ccursor = COOP.cursor()
    ASOS = get_dbconn("asos")
    acursor = ASOS.cursor()

    # Get records
    ccursor.execute(
        "SELECT valid, max_high_yr, max_high from climate where "
        "station = 'IA2203' and max_high_yr > 1932"
    )

    hjday = []
    htime = []

    for row in ccursor:
        d = "%s-%s" % (row[1], row[0].strftime("%m-%d"))
        high = row[2]
        acursor.execute(
            """SELECT valid, tmpf from t%s WHERE
        station = 'DSM' and valid >= '%s 00:00'
        and valid < '%s 23:59' and tmpf > %s - 4 ORDER by tmpf DESC LIMIT 1
            """
            % (row[1], d, d, high)
        )
        row2 = acursor.fetchone()
        if row2 is None:
            continue
        hjday.append(int(row2[0].strftime("%j")))
        htime.append(row2[0].hour * 60 + row2[0].minute)

    # Get records
    ccursor.execute(
        """
    SELECT valid, min_low_yr, min_low from climate where station = 'IA2203'
    and min_low_yr > 1932
    """
    )

    ljday = []
    ltime = []

    for row in ccursor:
        d = "%s-%s" % (row[1], row[0].strftime("%m-%d"))
        high = row[2]
        acursor.execute(
            """SELECT valid, tmpf from t%s WHERE
        station = 'DSM' and valid >= '%s 00:00'
        and valid < '%s 23:59' and tmpf < %s + 4 ORDER by tmpf ASC LIMIT 1"""
            % (row[1], d, d, high)
        )
        row2 = acursor.fetchone()
        if row2 is None:
            continue
        if row2[0].hour > 12 and row2[0].hour < 18:
            print(row2)
        ljday.append(int(row2[0].strftime("%j")))
        ltime.append(row2[0].hour * 60 + row2[0].minute)

    (fig, ax) = plt.subplots(1, 1)

    ax.scatter(hjday, htime, color="r", label="High")
    ax.scatter(ljday, ltime, color="b", label="Low")
    ax.scatter(315, 12 * 60 + 35, color="r", marker="x", label="Today")
    ax.set_title(
        "Estimated Time of Day of Record High/Low Temperature\n"
        "for Des Moines records set after 1932 to 10 Nov 2012"
    )
    ax.set_xlim(0, 366)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(month_abbr[1:])
    ax.set_yticklabels(("Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM", "Mid"))
    ax.set_yticks(range(0, 1441, 240))
    ax.set_ylabel("Local Time of Day CST/CDT")
    ax.set_ylim(-1, 1440)
    ax.legend(loc=(0.45, 0.8))
    ax.grid(True)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
