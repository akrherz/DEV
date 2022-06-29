"""Look into day to day changes in soil temperature"""

from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
import numpy as np
from scipy import stats
from pandas.io.sql import read_sql


def magic(ax, xvals, yvals):
    """You can do magic"""
    slope, intercept, r_value, _p_value, _std_err = stats.linregress(
        xvals, yvals
    )
    ax.scatter(xvals, yvals)
    xpts = np.array(ax.get_xlim())
    ax.plot(xpts, slope * xpts + intercept, color="r")
    ax.text(
        1.1,
        0.01,
        "Slope: %.1f R$^2$= %.1f" % (slope, r_value**2),
        ha="right",
        bbox=dict(color="w"),
        transform=ax.transAxes,
    )


def main():
    """Go Main Go"""
    pgconn = get_dbconn("isuag")
    df = read_sql(
        """
        select valid, extract(month from valid) as month,
        c11 as high, c12 as low, c30 as soilt, c80 / 23.90 as rad,
        lag(c11) OVER (ORDER by valid ASC) as lag_high,
        lag(c12) OVER (ORDER by valid ASC) as lag_low,
        lag(c30) OVER (ORDER by valid ASC) as lag_soilt,
        lag(c80 / 23.90) OVER (ORDER by valid ASC) as lag_rad
        from daily where station = 'A130209' ORDER by valid ASC
        """,
        pgconn,
        index_col="valid",
    )
    df["avgt"] = (df["high"] + df["low"]) / 2.0
    df["lag_avgt"] = (df["lag_high"] + df["lag_low"]) / 2.0
    df["soilt_diff"] = df["soilt"] - df["lag_soilt"]
    df["rad_diff"] = df["rad"] - df["lag_rad"]
    df["soilt_diff"] = df["soilt"] - df["lag_soilt"]
    df["avgt_diff"] = df["avgt"] - df["lag_avgt"]

    april = df[(df["month"] == 4) & (df["soilt"] > 32)]
    fig = plt.figure(figsize=(8, 6))
    fig.text(
        0.5,
        0.95,
        (
            "Ames ISU Ag Climate Station 1986-2014\n"
            "April Daily 4inch Depth Soil Temperature "
            "(non-frozen) Day to Day (D2D) Changes"
        ),
        ha="center",
        va="center",
    )
    height = 0.35
    ax = fig.add_axes([0.1, 0.55, height, height])
    magic(ax, april["avgt_diff"], april["soilt_diff"])
    ax.grid(True)
    ax.set_ylabel("D2D Change in 4in Soil Temp [F]")
    ax.set_xlabel("D2D Change in Avg Air Temp [F]")

    ax = fig.add_axes([0.6, 0.55, height, height])
    magic(ax, april["rad_diff"], april["soilt_diff"])
    ax.grid(True)
    ax.set_ylabel("D2D Change in 4in Soil Temp [F]")
    ax.set_xlabel("D2D Change in Radiation [MJ/m2]")

    ax = fig.add_axes([0.1, 0.1, height, height])
    magic(ax, april["rad"], april["soilt_diff"])
    ax.grid(True)
    ax.set_ylabel("D2D Change in 4in Soil Temp [F]")
    ax.set_xlabel("Daily Radiation [MJ/m2]")

    ax = fig.add_axes([0.6, 0.1, height, height])
    magic(ax, april["avgt"], april["soilt"])
    ax.set_xlabel("Avg Air Temp [F]")
    ax.set_ylabel("Avg 4inch Soil Temp [F]")
    ax.grid(True)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
