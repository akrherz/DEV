"""Plot of archived data."""
import datetime

import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
from pyiem.datatypes import speed, pressure


def main():
    """Go Main"""
    pgconn = get_dbconn("asos")
    df = read_sql(
        "SELECT valid, drct, sknt, gust, alti, tmpf, dwpf from t2019 "
        "where station = %s and valid >= '2019-06-28 08:30' and "
        "valid <= '2019-06-28 13:15' ORDER by valid ASC",
        pgconn,
        params=("MXO",),
        index_col="valid",
    )
    xticks = []
    xticklabels = []
    for valid in pd.date_range(df.index.min(), df.index.max(), freq="1min"):
        if pd.to_datetime(valid).minute % 30 == 0:
            xticks.append(valid)
            ts = pd.to_datetime(valid) - datetime.timedelta(hours=5)
            xticklabels.append(ts.strftime("%-I:%M\n%p"))

    fig = plt.figure(figsize=(6, 7))
    ax1 = fig.add_axes([0.1, 0.55, 0.75, 0.35])
    ax1.plot(df.index.values, df["tmpf"], label="Air Temp")
    ax1.plot(df.index.values, df["dwpf"], label="Dew Point")
    ax1.legend()
    ax1.grid(True)
    ax1.set_ylabel(r"Temperature $^\circ$F")
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(xticklabels)
    ax1.set_title(
        (
            "Monticello, IA (KMXO) AWOS Observations for 28 Jun 2019\n"
            "Heat Burst Event, "
            r"Max Temp: %.1f$^\circ$F Min Dewpoint: %.1f$^\circ$F"
        )
        % (df["tmpf"].max(), df["dwpf"].min())
    )

    ax = fig.add_axes([0.1, 0.08, 0.75, 0.35])

    ax.bar(
        df.index.values,
        speed(df["gust"], "KT").value("MPH"),
        width=10 / 1440.0,
        color="red",
    )
    ax.bar(
        df.index.values,
        speed(df["sknt"], "KT").value("MPH"),
        width=10 / 1440.0,
        color="tan",
    )
    ax.set_ylabel("Wind Speed (tan) & Gust (red) [mph]")
    ax.grid(True, zorder=5)
    ax.set_ylim(0, 60)

    ax2 = ax.twinx()
    ax2.plot(
        df.index.values,
        pressure(df["alti"], "IN").value("MB"),
        color="g",
        lw=2,
    )
    ax2.set_ylabel("Altimeter [inch]", color="green")
    ax2.set_xticks(xticks)
    ax2.set_xticklabels(xticklabels)
    ax.set_xlabel("28 June 2019 CDT")
    ax.set_xlim(*ax1.get_xlim())

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
