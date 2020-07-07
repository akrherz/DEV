"""Generate a plot of an OT station for feature purposes"""

from pyiem.util import get_dbconn
import numpy as np
import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.io.sql import read_sql


def main():
    """Go Main Go"""
    pgconn = get_dbconn("other")
    df = read_sql(
        """
    select valid, tmpf, sknt,
    drct from t2017 where station = 'OT0010'
    and valid > '2017-10-06 16:00' and valid < '2017-10-07 10:00'
    ORDER by valid ASC
    """,
        pgconn,
    )

    (fig, ax) = plt.subplots(1, 1)
    ax.plot(df["valid"].values, df["tmpf"].values, zorder=5)
    ax.grid(True)
    ax2 = ax.twinx()
    ax2.scatter(df["valid"].values, df["drct"].values, color="red", zorder=3)
    ax2.set_ylim(0, 360)
    ax2.set_yticks(range(0, 361, 45))
    ax2.set_yticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax.set_ylim(58, 72)
    ax.set_yticks(np.linspace(58, 72, 9))
    ax.set_ylabel(r"Air Temperature $^\circ$F", color="blue")
    ax2.set_ylabel("Wind Direction", color="red")
    ax.set_title(
        (
            "ISU AMS Weather Station 6-7 Oct 2017\n"
            "Station located on the roof of Agronomy Hall, Iowa State"
        )
    )
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%-I %p", tz=pytz.timezone("America/Chicago"))
    )
    ax.set_xlabel("Evening of 6 October till morning of 7 October 2017")
    # so annoying
    ax.set_zorder(ax2.get_zorder() + 1)
    ax.patch.set_visible(False)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
