"""Plot timeseries of CLI data."""
import matplotlib.dates as mdates
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn

STATIONS = {
    "KDSM": "Des Moines",
    "KDBQ": "Dubuque",
    "KSUX": "Sioux City",
    "KMCW": "Mason City",
    "KMLI": "Moline, IL",
    "KOMA": "Omaha, NE",
}


def main():
    """Go Main Go."""
    pgconn = get_dbconn("iem")
    df = read_sql(
        """
    SELECT valid, station, precip_jan1 - precip_jan1_normal as departure
    from cli_data WHERE valid > '2020-01-01' and station in
    ('KDSM', 'KDBQ', 'KSUX', 'KMCW', 'KMLI', 'KOMA') ORDER by valid ASC
    """,
        pgconn,
        index_col=None,
    )

    (fig, ax) = plt.subplots(1, 1)
    for station, gdf in df.groupby("station"):
        vals = gdf["departure"].values
        ax.plot(
            gdf["valid"].values,
            vals,
            label=f'{STATIONS[station]} {vals[-1]:.2f}"',
            lw=2,
        )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.grid(True)
    ax.legend(loc=3)
    ax.set_title(
        (
            "2020 Year to Date Precipitation Departures\n"
            "Data from NWS CLI Reporting Sites"
        )
    )
    ax.set_ylabel("Precipitation Departure [inch]")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
