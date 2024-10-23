"""Plot of 1minute ASOS data.

TODO: roll this visualization into autoplot 211
"""

import datetime

import matplotlib.dates as mdates
import pandas as pd
import pytz
from matplotlib.patches import Rectangle
from pyiem.plot.use_agg import plt
from pyiem.util import get_sqlalchemy_conn, utc


def shade(ax):
    """Draw the axspans for the passage times."""
    ebbase = utc(2022, 1, 15, 14, 15)
    wbbase = utc(2022, 1, 16, 7, 0)
    width = datetime.timedelta(minutes=15)
    period = 35.0 * 60.0
    for passage in range(5):
        ax.axvspan(
            ebbase + datetime.timedelta(minutes=passage * period) - width,
            ebbase + datetime.timedelta(minutes=passage * period) + width,
            color="pink",
        )
        ax.axvspan(
            wbbase + datetime.timedelta(minutes=passage * period) - width,
            wbbase + datetime.timedelta(minutes=passage * period) + width,
            color="lightblue",
        )


def main():
    """Go Main"""
    with get_sqlalchemy_conn("asos1min") as conn:
        df = pd.read_sql(
            """
        SELECT valid, pres1 from t202201_1minute
        where station = %s and valid >= '2022-01-15 0:00' and
        valid <= '2022-01-21 23:59' ORDER by valid ASC
        """,
            conn,
            params=("AMW",),
            index_col="valid",
        )
    # Fill out the dataframe to have obs every minutes
    df = df.resample("1min").interpolate()

    CST = pytz.timezone("America/Chicago")
    xlocator = mdates.HourLocator(range(0, 24, 12), tz=CST)
    xformater = mdates.DateFormatter("%I %p\n%b%-d", tz=CST)
    x0 = 0.09
    xwidth = 0.88

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_axes([x0, 0.51, xwidth, 0.35])
    ax.plot(df.index.values, df["pres1"], color="k")
    ax.xaxis.set_major_locator(xlocator)
    ax.xaxis.set_major_formatter(xformater)
    ax.grid(True)
    ax.set_ylabel("Pressure Altimeter (in)")
    fig.text(
        0.5,
        0.99,
        "15-21 January 2022 - Pressure Altimeter Timeseries for Ames\n"
        "Data Source: NCEI/NWS One Minute ASOS\n"
        "Estimated wave passage with 35 hour return interval",
        ha="center",
        va="top",
        fontsize=14,
    )
    ax.legend(
        [
            Rectangle((0, 0), 1, 1, fc="pink"),
            Rectangle((0, 0), 1, 1, fc="lightblue"),
        ],
        ["Eastbound", "Westbound"],
        loc=[-0.07, 1.01],
        ncol=1,
    )
    ax.set_xlim(df.index.values[0], df.index.values[-1])
    shade(ax)

    gdf = df - df.rolling(15, center=True).mean()
    ax = fig.add_axes([x0, 0.08, xwidth, 0.35])
    ax.plot(gdf.index.values, gdf["pres1"], color="k")
    ax.xaxis.set_major_locator(xlocator)
    ax.xaxis.set_major_formatter(xformater)
    ax.grid(True)
    ax.set_xlim(df.index.values[0], df.index.values[-1])
    ax.set_ylabel("Alimeter - 15min Avg (in)")
    shade(ax)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
