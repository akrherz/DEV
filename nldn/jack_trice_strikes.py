"""The 30 minute shot clock."""
import datetime

from pyiem.util import get_sqlalchemy_conn
from pyiem.plot import figure_axes
import pandas as pd

JACK_TRICE = [-93.6379, 42.0140]
KINNICK = [-91.55106, 41.65863]


def get_data():
    """Fetch."""
    with get_sqlalchemy_conn("nldn") as conn:
        df = pd.read_sql(
            """
            select distinct date_trunc('minute', valid) as dt from
            nldn2022_09 where valid > '2022-09-17 12:00' and
            valid < '2022-09-18 04:00' and st_distance(
                ST_GeomFromEWKT('SRID=4326;POINT(%s %s)')::geography,
                geom::geography) < 12874.8 ORDER by dt ASC
        """,
            conn,
            params=KINNICK,
            index_col=None,
        )
    df.to_csv("data.csv")


def main():
    """Go Main Go."""
    # get_data()
    df = pd.read_csv("data.csv")
    df["dt"] = pd.to_datetime(df["dt"]) - datetime.timedelta(hours=5)
    df["s"] = df["dt"].dt.strftime("%Y%m%d%H%M")
    x = []
    y = []
    sts = datetime.datetime(2022, 9, 17, 17)
    ets = datetime.datetime(2022, 9, 18, 2)
    interval = datetime.timedelta(minutes=1)
    now = sts
    current = None
    xticks = []
    xticklabels = []
    while now < ets:
        if now.minute == 0:
            xticks.append(now)
            xticklabels.append(now.strftime("%-I %p"))
        x.append(now)
        if now.strftime("%Y%m%d%H%M") in df["s"].values:
            current = 0
        else:
            if current is not None:
                current += 1
        y.append(current)
        now += interval

    (fig, ax) = figure_axes(
        apctx={"_r": "43"},
    )
    ax.plot(x, y, zorder=6)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_yticks(list(range(0, 91, 15)))
    ax.set_ylabel("Minutes since Last Lightning Strike", fontsize=16)
    ax.set_xlabel(
        "Evening of 17 September 2022 (CDT), approximate game delays shaded",
        fontsize=16,
    )
    ax.axhline(30, lw=2, color="r")
    ax.set_ylim(bottom=-0.1, top=91)
    ax.axvspan(
        datetime.datetime(2022, 9, 17, 22, 7),
        datetime.datetime(2022, 9, 17, 23, 55),  # Not likely right
        color="k",
        alpha=0.4,
        zorder=2,
    )
    ax.axvspan(
        datetime.datetime(2022, 9, 17, 23, 57),
        datetime.datetime(2022, 9, 18, 0, 33),  # 12 minute warmup?
        color="k",
        alpha=0.4,
        zorder=2,
    )
    ax.axvspan(
        datetime.datetime(2022, 9, 17, 20, 43),
        datetime.datetime(2022, 9, 17, 21, 44),  # 12 minute warmup
        color="k",
        alpha=0.4,
        zorder=2,
    )
    ax.set_xlim(
        datetime.datetime(2022, 9, 17, 18, 30),
        datetime.datetime(2022, 9, 18, 1, 30),
    )
    ax.grid(True)
    ax.set_title(
        (
            "Nevada vs Iowa Football Game\n"
            "Time since Last Lightning Strike within 8 miles "
            "of Kinnick Stadium\n"
            "Data courtesy of National Lightning Detection Network"
        )
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
