"""A long term plot."""

import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import get_sqlalchemy_conn


def plot():
    """Plot things."""
    df = pd.read_csv(
        "/tmp/memt1.csv",
        parse_dates=[
            "ts",
        ],
    )
    print(df.value.describe())
    fig, ax = figure_axes(
        apctx={"_r": "43"},
        title="Mississippi River at Memphis (MEMT1)",
        subtitle=(
            "Unofficial IEM archives (late 2010-2022) "
            "of NWS relayed SHEF reports"
        ),
    )
    df2 = df[df.value > -99]
    ax.plot(df2.ts, df2.value)
    ax.axhline(df2.value.values[-1], color="r", linestyle="-.")
    ax.text(
        1,
        0.05,
        f"Last:\n{df2.value.values[-1]:.2f}'",
        transform=ax.transAxes,
        color="r",
    )
    ax.grid(True)
    ax.set_ylabel("Gage Height [ft]")
    ax.set_xlabel("*till 9 PM 17 Oct 2022 CDT")
    fig.savefig("221018.png")


def dump():
    """Dump things."""
    with get_sqlalchemy_conn("hads") as conn:
        df = pd.read_sql(
            "select valid at time zone 'utc' as ts, value from raw where "
            "station = 'MEMT1' and key in ('HGIRGZ', 'HGIRGZZ') "
            "order by valid asc",
            conn,
        )
    df.to_csv("/tmp/memt1.csv", index=False)


if __name__ == "__main__":
    plot()
