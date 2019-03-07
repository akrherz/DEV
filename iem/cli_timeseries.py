"""Plot timeseries of CLI data."""
from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn

STATIONS = {
    'KDSM': 'Des Moines',
    'KDBQ': 'Dubuque',
    'KSUX': 'Sioux City',
    'KMCW': 'Mason City',
    'KMLI': 'Moline, IL',
    'KOMA': 'Omaha, NE'
}


def main():
    """Go Main Go."""
    pgconn = get_dbconn('iem')
    df = read_sql("""
    SELECT valid, station, snow_jul1 - snow_jul1_normal as departure
    from cli_data WHERE valid > '2018-10-01' and station in
    ('KDSM', 'KDBQ', 'KSUX', 'KMCW', 'KMLI', 'KOMA') ORDER by valid ASC
    """, pgconn, index_col=None)

    (fig, ax) = plt.subplots(1, 1)
    for station, gdf in df.groupby('station'):
        ax.plot(
            gdf['valid'].values, gdf['departure'].values,
            label=STATIONS[station], lw=2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(True)
    ax.legend(loc=2)
    ax.set_title(
        ("Season to Date Snowfall Departures\n"
         "Data from NWS CLI Reporting Sites"))
    ax.set_ylabel("Snowfall Departure [inch]")
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
