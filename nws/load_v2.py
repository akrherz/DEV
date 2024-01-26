"""Warning load by minute"""
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes
from pyiem.util import utc

TZ = ZoneInfo("America/Chicago")


def main():
    """Do Query"""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            """
        WITH data as (select w.ugc, u.area2163 * 0.386 as area,
        generate_series(issue, expire, '1 minute'::interval) as ts from
        warnings_2024 w JOIN ugcs u on (w.gid = u.gid)
        where phenomena = 'FG' and significance = 'Y' and
        issue > '2024-01-10' and substr(w.ugc, 1, 2) != 'AK')
        SELECT ts, count(*), sum(area) / 3119884. * 100. as cus
        from data GROUP by ts ORDER by ts ASC
            """,
            conn,
            index_col=None,
            parse_dates="ts",
        )

    (fig, ax) = figure_axes(
        title="NWS Forecast Zones Under Dense Fog Advisory",
        subtitle="Based on Unofficial IEM Archives, till 5 AM 26 Jan 2024",
        figsize=(8, 6),
    )
    ax.set_position([0.1, 0.53, 0.8, 0.35])
    ax.bar(df["ts"].values, df["count"].values, width=1 / 1440.0)

    ax.grid(True)
    ax.set_xlim(utc(2024, 1, 23), utc(2024, 1, 26, 11))
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12], tz=TZ))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I %p\n%-d %b", tz=TZ))

    # Place a horinzontal line at the max value and label it
    maxval = df["count"].max()
    ax.axhline(maxval, lw=2, color="r", zorder=1)
    ax.text(
        utc(2024, 1, 26, 12),
        maxval,
        f"Max:\n{maxval}",
        va="center",
        ha="left",
        color="r",
    )

    ax.set_ylabel("Number of Zones")
    ax.set_ylim(bottom=0.1)

    ax = fig.add_axes([0.1, 0.1, 0.8, 0.35])
    ax.bar(df["ts"].values, df["cus"].values, width=1 / 1440.0)
    ax.set_ylabel("Percent of Contiguous US")
    ax.set_ylim(bottom=0)
    ax.grid(True)
    ax.set_xlim(utc(2024, 1, 23), utc(2024, 1, 26, 11))
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12], tz=TZ))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I %p\n%-d %b", tz=TZ))
    ax.set_xlabel("Valid Time (America/Chicago)")
    maxval = df["cus"].max()
    ax.axhline(maxval, lw=2, color="r", zorder=1)
    ax.text(
        utc(2024, 1, 26, 12),
        maxval,
        f"Max:\n{maxval:.1f}%",
        va="center",
        ha="left",
        color="r",
    )

    fig.savefig("240126.png")


if __name__ == "__main__":
    main()
