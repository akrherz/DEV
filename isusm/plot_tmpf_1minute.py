"""Generate a plot of 1minute data."""

import pytz

import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from metpy.calc import dewpoint_from_relative_humidity
from metpy.units import units
from pandas.io.sql import read_sql
from pyiem.plot import figure_axes
from pyiem.util import get_dbconn, utc


def main():
    """Go Main Go."""
    pgconn = get_dbconn("isuag")
    df = read_sql(
        """
        SELECT valid, tair_c_avg_qc, rh_avg_qc, winddir_d1_wvt_qc,
        ws_mph_s_wvt_qc from sm_minute where station = 'CNAI4'
        and valid >= '2021-03-10 08:00' and valid < '2021-03-10 20:00'
        ORDER by valid ASC
    """,
        pgconn,
        index_col="valid",
    )
    tmpc = df["tair_c_avg_qc"].values * units("degC")
    df["tmpf"] = tmpc.to(units("degF")).m
    df["dwpf"] = (
        dewpoint_from_relative_humidity(
            tmpc,
            df["rh_avg_qc"].values * units("percent"),
        )
        .to(units("degF"))
        .m
    )
    title = "ISU Soil Moisture 10 Mar 2021 -- Western ISU Farm near Castana"
    subtitle = "One Minute Time Series between 8 AM and 8 PM CST"
    (fig, ax) = figure_axes(title=title, subtitle=subtitle)
    ax.set_position([0.05, 0.5, 0.9, 0.4])
    x = df.index.values
    ax.plot(x, df["tmpf"].values, color="r")
    ax.plot(x, df["dwpf"].values, color="b")
    ax.set_ylim(30, 80)
    ax.annotate(
        "Approximate\nDry Line Passage",
        xy=(utc(2021, 3, 10, 17, 45), 55),
        xytext=(-50, -50),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="0.8"),
        arrowprops=dict(
            arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=1"
        ),
    )
    ax.annotate(
        "Cold Front Passage",
        xy=(utc(2021, 3, 10, 20), 38),
        xytext=(30, -20),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="0.8"),
        arrowprops=dict(
            arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=1"
        ),
    )
    ax2 = ax.twinx()
    ax2.plot(x, df["rh_avg_qc"].values, color="g")
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("Relative Humidity [%]", color="g")
    lines = [
        Line2D([0], [0], color="r", lw=2),
        Line2D([0], [0], color="b", lw=2),
        Line2D([0], [0], color="g", lw=2),
    ]
    ax.legend(lines, ["Air Temp", "Dew Point", "RH%"], loc=3)
    tz = pytz.timezone("America/Chicago")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%I %p", tz=tz))
    ax.grid()
    ax.set_ylabel(r"Temperature $^\circ$F")

    # Second
    ax = fig.add_axes([0.05, 0.1, 0.9, 0.35])
    ax.plot(x, df["ws_mph_s_wvt_qc"].values, color="k")
    ax.set_ylim(0, 40)
    ax.set_ylabel("One Min Avg Wind Speed [MPH]")
    ax.grid(True)

    ax2 = ax.twinx()
    ax2.scatter(x, df["winddir_d1_wvt_qc"].values, s=10, color="b")
    ax2.set_ylim(0, 360)
    ax2.set_yticks(range(0, 361, 45))
    ax2.set_yticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax2.set_ylabel("Wind Direction", color="b")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%I %p", tz=tz))
    ax.set_xlabel("Central Standard Time on 10 March 2021")

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
