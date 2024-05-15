"""One off plot of AQI from our purpleair site."""

import pandas as pd
from matplotlib.dates import DateFormatter
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes


def main():
    """GO Main."""
    with get_sqlalchemy_conn("other") as conn:
        df = pd.read_sql(
            """
        select date(valid), min(pm2_5_aqi_b), avg(pm2_5_aqi_b),
        max(pm2_5_aqi_b) from purpleair group by date order by date            
""",
            conn,
        )

    (fig, ax) = figure_axes(
        title="Ames, IA ISU Agronomy Hall Purple Air PM2.5 AQI",
        figsize=(8, 6),
    )
    ax.set_position([0.1, 0.1, 0.7, 0.8])

    ax.bar(
        df["date"],
        df["max"] - df["min"],
        bottom=df["min"],
        color="k",
        zorder=2,
        label="Daily Min/Max Range",
    )
    ax.grid(True)

    ax.set_ylabel("PM2.5 Air Quality Index")
    ax.axhspan(0, 50, color="green", alpha=0.5, zorder=1)
    ax.annotate(
        "Good",
        xy=(1.01, 25),
        xycoords=("axes fraction", "data"),
    )
    ax.axhspan(50, 100, color="yellow", alpha=0.5, zorder=1)
    ax.annotate(
        "Moderate",
        xy=(1.01, 75),
        xycoords=("axes fraction", "data"),
    )
    ax.axhspan(100, 150, color="orange", alpha=0.5, zorder=1)
    ax.annotate(
        "Unhealthy for\nSensitive Groups",
        xy=(1.01, 125),
        va="center",
        xycoords=("axes fraction", "data"),
    )
    ax.axhspan(150, 200, color="red", alpha=0.5, zorder=1)
    ax.annotate(
        "Unhealthy",
        xy=(1.01, 175),
        xycoords=("axes fraction", "data"),
    )
    ax.axhspan(200, 300, color="purple", alpha=0.5, zorder=1)
    ax.annotate(
        "Very Unhealthy",
        xy=(1.01, 250),
        xycoords=("axes fraction", "data"),
    )
    ax.axhspan(300, 500, color="maroon", alpha=0.5, zorder=1)
    ax.annotate(
        "Hazardous",
        xy=(1.01, 375),
        xycoords=("axes fraction", "data"),
    )

    ax.set_ylim(0, 500)
    ax.legend(loc=2)
    ax.xaxis.set_major_formatter(DateFormatter("%-d\n%b"))
    fig.savefig("240515.png")


if __name__ == "__main__":
    main()
