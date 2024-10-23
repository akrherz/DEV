"""Plot some vwc please."""

import matplotlib.dates as mdates
import pandas as pd
import pytz
from pandas.io.sql import read_sql
from pyiem.plot import figure_axes
from pyiem.util import get_dbconn

CENTRAL = pytz.timezone("America/Chicago")


def main():
    """Go Main Go."""
    pgconn = get_dbconn("isuag")
    df = read_sql(
        "SELECT * from sm_minute where station = 'BOOI4' "
        "and valid > '2021-05-08 19:00' ORDER by valid ASC",
        pgconn,
        index_col="valid",
    )
    fig, ax = figure_axes(
        title="ISU Soil Moisture Network :: ISU Ag Farm west of Ames",
        subtitle=(
            "Soil Moisture Response at Depth to 0.64 inches of Precipitation"
        ),
    )
    ax.set_position([0.1, 0.1, 0.75, 0.8])
    ax2 = ax.twinx()
    ax2.plot(
        df.index.values,
        df["rain_in_tot"].cumsum(),
        linestyle=":",
        lw=3,
        color="k",
    )
    ax2.set_ylim(bottom=0)
    ax2.set_ylabel("Accumulated Precipitation inch (dashed line)")
    df = df[~pd.isna(df["vwc2"])]
    df = df.rolling(5).mean()
    for level in [2, 4, 8, 12, 16, 20, 24, 30, 40]:
        ax.plot(
            df.index.values,
            df[f"vwc{level}"].values,
            label=f"{level} inch",
            lw=3 if level < 10 else 1,
        )
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%-I %p\n%-d %b", tz=CENTRAL)
    )
    ax.set_ylabel("Soil Volumetric Water Content [m^3/m^3]")
    ax.legend(loc=(1.08, 0.5), ncol=1)
    ax.set_xlabel("7-9 May 2021 :: Central Daylight Time")
    ax.grid(True)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
