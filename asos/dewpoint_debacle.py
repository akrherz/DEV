"""Le Sigh."""

from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import pandas as pd
from matplotlib.axes import Axes
from metpy.calc import dewpoint_from_relative_humidity
from metpy.units import units
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure
from pyiem.util import utc

CST = ZoneInfo("America/Chicago")


def common(ax: Axes, df2: pd.DataFrame, label):
    """Plot..."""
    maxval = df2["dwpf"].max()
    ax.plot(df2.valid, df2.tmpf, color="r")
    ax.plot(df2.valid, df2.dwpf, color="g")
    ax.axhline(maxval, color="k", lw=1, ls="--")
    ax.set_ylim(60, 101)
    ax.set_yticks(range(60, 101, 5))
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 6), tz=CST))
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%-m/%-d\n%-I %p", tz=CST)
    )
    ax.axvspan(
        utc(2026, 7, 26, 11, 30),
        utc(2026, 7, 26, 17),
        color="pink",
    )
    ax.axvspan(
        utc(2026, 7, 26, 23),
        utc(2026, 7, 27, 1, 30),
        color="lightblue",
    )
    ax.axvspan(
        utc(2026, 7, 27, 11, 30),
        utc(2026, 7, 27, 17),
        color="pink",
    )
    ax.axvspan(
        utc(2026, 7, 27, 23),
        utc(2026, 7, 28, 1, 30),
        color="lightblue",
    )
    ax.annotate(
        f"{label} Max Dewpt:{maxval:.1f}°F",
        xy=(0.02, 0.96),
        xycoords="axes fraction",
        ha="left",
        va="bottom",
        color="b",
        bbox={"facecolor": "white", "alpha": 1, "pad": 2, "edgecolor": "k"},
        fontsize=10,
    )
    ax.set_ylabel("Air/Dewpt Temperature °F")


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("asos1min") as conn:
        amwdf = pd.read_sql(
            """
            select valid, tmpf, dwpf from alldata_1minute where station = 'AMW'
            and valid >= '2026-07-26' and valid <= '2026-07-28'
            ORDER by valid asc
            """,
            conn,
        )
    with get_sqlalchemy_conn("isuag") as conn:
        knai4df = pd.read_sql(
            """
            select valid, tair_c_avg_qc, rh_avg_qc from sm_minute
            where station = 'KNAI4'
            and valid > '2026-07-26' and valid < '2026-07-28'
            ORDER by valid asc
            """,
            conn,
        )
        knai4df["tmpf"] = (
            (units("degC") * knai4df["tair_c_avg_qc"].to_numpy())
            .to(units("degF"))
            .m
        )
        knai4df["dwpf"] = (
            dewpoint_from_relative_humidity(
                units("degC") * knai4df["tair_c_avg_qc"].to_numpy(),
                knai4df["rh_avg_qc"].to_numpy() * units.percent,
            )
            .to(units("degF"))
            .m
        )

    with get_sqlalchemy_conn("asos") as conn:
        axadf = pd.read_sql(
            """
            select valid, tmpf, dwpf from alldata
            where station = 'AXA'
            and valid > '2026-07-26' and valid < '2026-07-28'
            ORDER by valid asc
            """,
            conn,
        )

    fig = figure(
        title="26-27 July 2026 :: Air + Dew Point Temperature Time Series",
        subtitle="Times in CDT, dashed line shows max dew point level",
        figsize=(8, 7),
    )
    ysz = 0.22
    y0 = 0.06
    ypad = 0.08
    ax = fig.add_axes((0.1, y0, 0.85, ysz))
    common(ax, axadf, "KAXA Algona, IA ASOS")
    ax.set_xlim(amwdf.valid.values[0], amwdf.valid.values[-1])

    ax2 = fig.add_axes((0.1, y0 + ysz + ypad, 0.85, ysz))
    common(ax2, amwdf, "KAMW Ames, IA ASOS")
    ax2.set_xlim(*ax.get_xlim())

    ax3 = fig.add_axes((0.1, y0 + 2 * (ysz + ypad), 0.85, ysz))
    common(ax3, knai4df, "KNAI4 Kanawha ISU Farm, IA")
    ax3.set_xlim(*ax.get_xlim())

    fig.savefig("260731.png")


if __name__ == "__main__":
    main()
