"""An old plot."""
import datetime

from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt
import pytz
import numpy
import matplotlib.dates as mdates


def main():
    """Go Main Go."""
    IEM = get_dbconn("iem")
    icursor = IEM.cursor()
    MOS = get_dbconn("mos")
    mcursor = MOS.cursor()

    jan1 = datetime.datetime(2013, 1, 1)
    jan1 = jan1.replace(tzinfo=pytz.UTC)
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.UTC)
    hourly_obs = numpy.zeros((24 * 367), "f")

    icursor.execute(
        "SELECT valid, phour from hourly_2013 WHERE station = 'DVN' "
        "and phour > 0"
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
    select runtime, sum(precip), max(ftime) from model_gridpoint_2013
    WHERE station = 'KDVN'
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
            diffs.append((row[1] / 25.4) - numpy.sum(hourly_obs[idx:idx2]))
        dates.append(row[0])
        fx.append(row[1] / 25.4)

    (fig, ax) = plt.subplots(2, 1, sharex=True)
    ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    ax[0].bar(dates, fx, width=0.25, fc="b", ec="b")
    ax[0].set_ylabel("Model Forecast [inch]")
    ax[0].set_title("NAM 96 Hour Gridded Precipitation Forecast for Davenport")
    ax[0].grid(True)

    bars = ax[1].bar(dates, diffs, width=0.25, ec="b", fc="b")
    ax[1].bar(
        xdates, xvals, bottom=xbot, width=0.25, ec="#EEEEEE", fc="#EEEEEE"
    )
    ax[1].set_ylabel("Model - Obs Difference [inch]")
    for i, mybar in enumerate(bars):
        if diffs[i] < 0:
            mybar.set_facecolor("r")
            mybar.set_edgecolor("r")
    ax[1].grid(True)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
