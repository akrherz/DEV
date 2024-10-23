"""Plot period of record VWC."""

import matplotlib.dates as mdates
import pytz
from pandas.io.sql import read_sql
from pyiem.plot import figure_axes
from pyiem.util import get_dbconn

CENTRAL = pytz.timezone("America/Chicago")


def main():
    """Go Main Go."""
    pgconn = get_dbconn("isuag")
    df = read_sql(
        "SELECT valid, vwc_12_avg_qc, vwc_24_avg_qc, vwc_50_avg_qc "
        "from sm_hourly where station = 'NASI4' "
        "ORDER by valid ASC",
        pgconn,
        index_col="valid",
    )
    fig, ax = figure_axes(
        title="ISU Soil Moisture Network :: Nashua",
        subtitle=("Period of Record Hourly 50 inch Soil Moisture"),
    )
    ax.set_position([0.1, 0.1, 0.7, 0.8])
    for level in [12, 24, 50]:
        ax.plot(
            df.index.values,
            df[f"vwc_{level}_avg_qc"].values,
            label=(
                f"{level} inch {df[f'vwc_{level}_avg_qc'].min():.3f}-"
                f"{df[f'vwc_{level}_avg_qc'].max():.3f}"
            ),
            lw=3 if level < 10 else 1,
        )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y", tz=CENTRAL))
    ax.set_ylabel("Soil Volumetric Water Content [m^3/m^3]")
    ax.legend(loc=(1.0, 0.5), ncol=1)
    ax.grid(True)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
