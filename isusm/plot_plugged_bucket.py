"""Illustration of plugged Tipping Bucket."""

from pandas.io.sql import read_sql
from matplotlib.dates import DateFormatter, DayLocator
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn('isuag')
    df = read_sql("""
        SELECT valid, rain_mm_tot, rain_mm_tot_qc from sm_hourly WHERE
        station = 'CIRI4' and valid > '2019-03-29' ORDER by valid ASC
    """, pgconn, index_col='valid')

    (fig, ax) = plt.subplots(1, 1)
    ax.plot(
        df.index.values, df['rain_mm_tot'].cumsum() / 25.4, label="Obs")
    ax.plot(
        df.index.values, df['rain_mm_tot_qc'].cumsum() / 25.4,
        label="Estimates")
    ax.set_ylabel("Accumulated Precip [inch]")
    ax.xaxis.set_major_formatter(DateFormatter('%b %-d'))
    ax.xaxis.set_major_locator(DayLocator(bymonthday=range(1, 29, 7)))
    ax.set_ylim(bottom=-0.1)
    ax.set_xlabel("29 March - 30 April 2019")
    ax.grid(True)
    ax.legend()
    ax.set_title("ISU Soil Moisture :: Cedar Rapids Precipitation")
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
