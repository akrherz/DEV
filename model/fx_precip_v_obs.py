"""An old plot."""

import numpy as np

import matplotlib.dates as mdates
from pyiem.plot import figure
from pyiem.util import get_dbconn, utc


def main():
    """Go Main Go."""
    IEM = get_dbconn("iem")
    icursor = IEM.cursor()
    MOS = get_dbconn("mos")
    mcursor = MOS.cursor()

    jan1 = utc(2023, 1, 1)
    now = utc()
    hourly_obs = np.zeros((24 * 367), "f")

    icursor.execute("SET TIME ZONE 'UTC'")
    icursor.execute(
        """
        SELECT valid, phour from hourly_2023 h JOIN stations t on
        (h.iemid = t.iemid) WHERE t.id = 'DSM' and t.network = 'IA_ASOS'
        and phour > 0
        """
    )
    for row in icursor:
        delta = row[0] - jan1
        secs = delta.days * 86400.0 + delta.seconds
        idx = int(secs / 3600.0)
        hourly_obs[idx] = row[1]

    dates = []
    diffs = []
    fx = []
    mcursor.execute(
        """
    select runtime, sum(precip), max(ftime) from model_gridpoint_2023
    WHERE station = 'KDSM'
    and model = 'NAM' and precip < 100
    GROUP by runtime ORDER by runtime ASC
    """
    )
    xdates = []
    xvals = []
    xbot = []
    for row in mcursor:
        delta = row[0] - jan1
        secs = delta.days * 86400.0 + delta.seconds
        idx = int(secs / 3600.0)
        delta = row[2] - jan1
        secs = delta.days * 86400.0 + delta.seconds
        idx2 = int(secs / 3600.0)
        if row[2] > now:
            diffs.append(0)
            xdates.append(row[0])
            xvals.append(2.5)
            xbot.append(-1)
        else:
            diffs.append((row[1] / 25.4) - np.sum(hourly_obs[idx:idx2]))
        dates.append(row[0])
        fx.append(row[1] / 25.4)

    print(dates)
    fig = figure()
    ax = fig.add_axes([0.1, 0.6, 0.8, 0.3])
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    ax.bar(dates, fx, width=0.25, fc="b", ec="b")
    ax.set_ylabel("Model Forecast [inch]")
    ax.set_title("NAM 96 Hour Gridded Precipitation Forecast for Davenport")
    ax.grid(True)

    ax = fig.add_axes([0.1, 0.1, 0.8, 0.3])
    bars = ax.bar(dates, diffs, width=0.25, ec="b", fc="b")
    ax.bar(xdates, xvals, bottom=xbot, width=0.25, ec="#EEEEEE", fc="#EEEEEE")
    ax.set_ylabel("Model - Obs Difference [inch]")
    for i, mybar in enumerate(bars):
        if diffs[i] < 0:
            mybar.set_facecolor("r")
            mybar.set_edgecolor("r")
    ax.grid(True)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
