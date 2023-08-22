"""Le Sigh."""
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_sqlalchemy_conn, utc

CST = ZoneInfo("America/Chicago")


def common(ax, df2, label):
    """Plot..."""
    ax.plot(df2.valid, df2.tmpf, color="r")
    ax.plot(df2.valid, df2.dwpf, color="g")
    ax.set_ylim(63, 100)
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 4), tz=CST))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I %p", tz=CST))
    ax.axvspan(
        utc(2023, 8, 21, 11, 30),
        utc(2023, 8, 21, 17),
        color="pink",
    )
    ax.axvspan(
        utc(2023, 8, 21, 23),
        utc(2023, 8, 22, 1, 30),
        color="lightblue",
    )
    maxx = f"\nMax Dewpt:{df2.dwpf.max():.1f}"
    ax.text(
        0.02,
        0.8,
        label + maxx,
        transform=ax.transAxes,
        bbox={"color": "white"},
    )
    ax.set_ylabel(r"Air/Dewpt Temperature $^\circ$F")


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
            select id, valid, tmpf, dwpf from current_log c JOIN
            stations t on (c.iemid = t.iemid) where
            t.id in ('BOOI4', 'SUX', 'DNS') and tmpf is not null
            and dwpf is not null
            and valid > '2023-08-21' and valid < '2023-08-22'
            order by valid asc
            """,
            conn,
        )

    fig = figure(
        title="21 August 2023 :: Air + Dew Point Temperature Time Series",
        subtitle="Times in CDT",
        figsize=(8, 7),
    )
    ax = fig.add_axes([0.1, 0.05, 0.85, 0.25])
    df2 = df[df["id"] == "DNS"]
    common(ax, df2, "KDNS Denison, IA AWOS")
    ax.set_xlim(df.valid.values[0], df.valid.values[-1])

    ax = fig.add_axes([0.1, 0.35, 0.85, 0.25])
    df2 = df[df["id"] == "SUX"]
    common(ax, df2, "KSUX Sioux City, IA ASOS")
    ax.set_xlim(df.valid.values[0], df.valid.values[-1])

    ax = fig.add_axes([0.1, 0.65, 0.85, 0.25])
    df2 = df[df["id"] == "BOOI4"]
    common(ax, df2, "BOOI4 Ames AEA Farm, IA")
    ax.set_xlim(df.valid.values[0], df.valid.values[-1])

    fig.savefig("230822.png")


if __name__ == "__main__":
    main()
