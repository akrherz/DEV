"""Plot."""

import datetime

import matplotlib.pyplot as plt
import numpy as np
from pyiem.util import get_dbconn

ASOS = get_dbconn("asos1min")
cursor = ASOS.cursor()


def smooth(x, window_len=11, window="hanning"):
    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")
    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")
    if window_len < 3:
        return x
    if window not in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
        raise ValueError(
            "Window not 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
        )
    s = np.r_[
        2 * x[0] - x[(window_len - 1) :: -1],
        x,
        2 * x[-1] - x[-1:-window_len:-1],
    ]
    if window == "flat":  # moving average
        w = np.ones(window_len, "d")
    else:
        w = eval("np." + window + "(window_len)")
    y = np.convolve(w / w.sum(), s, mode="same")
    return y[window_len : (-window_len + 1)]


def get_day(ts):
    """erm."""
    cursor.execute(
        f"""SELECT extract(hour from valid) * 60.0 +
    extract(minute from valid), tmpf, valid from t{ts.year}_1minute
    where station = 'DSM' and date(valid) = %s ORDER by valid ASC
    """,
        (ts,),
    )
    if cursor.rowcount < 60:
        cursor.execute(
            f"""SELECT extract(hour from valid) * 60.0 +
    extract(minute from valid), tmpf, valid from t{ts.year}
    where station = 'DSM' and date(valid) = %s ORDER by valid ASC
    """,
            (ts,),
        )

    d = []
    t = []
    for row in cursor:
        d.append(row[0])
        t.append(row[1])

    if len(t) > 100:
        return np.array(d), smooth(np.array(t), 7)
    else:
        return np.array(d), np.array(t)


def main():
    """Go Main Go."""
    d1, t1 = get_day(datetime.datetime(2013, 8, 26))
    d2, t2 = get_day(datetime.datetime(2013, 8, 27))
    d3, t3 = get_day(datetime.datetime(2013, 8, 28))

    (fig, ax) = plt.subplots(1, 1)

    ax.plot(d1, t1, label="26 Aug", lw=2.0)
    ax.plot(d2, t2, label="27 Aug", lw=2.0)
    ax.plot(d3, t3, label="28 Aug", lw=2.0)
    ax.legend(loc=2)
    ax.grid(True)
    ax.set_xticks(np.arange(0, 8) * 180)
    ax.set_xticklabels(
        ["Mid", "3 AM", "6 AM", "9 AM", "Noon", "3 PM", "6 PM", "9 PM"]
    )
    ax.set_xlim(0, 1441)
    ax.set_title("Des Moines 26-28 August 2013 Temperature Timeseries")
    ax.set_ylabel(r"Temperature $^\circ$F")
    ax.set_xlabel("* Smooth applied to one minute time-series")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
