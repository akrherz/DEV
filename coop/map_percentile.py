"""Map values"""

from pandas.io.sql import read_sql
import psycopg2
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable


def main():
    """Go Main!"""
    nt = NetworkTable("WICLIMATE")
    pgconn = psycopg2.connect(database='coop', host='localhost', port=5555,
                              user='nobody')

    df = read_sql("""
        SELECT station, max(year) as val from alldata_wi where
        high >= 100 and substr(station, 3, 1) != 'C'
        and station != 'IA0000' GROUP by station
    """, pgconn, index_col='station')
    df['lat'] = 0.
    df['lon'] = 0.
    for station, _ in df.iterrows():
        if station in nt.sts:
            df.at[station, 'lat'] = nt.sts[station]['lat']
            df.at[station, 'lon'] = nt.sts[station]['lon']

    mp = MapPlot(title="Year of Last 100+ Daily High Temperature",
                 subtitle=('Valid up till 9 June 2017'), sector='state',
                 state='WI',
                 drawstates=True, continentalcolor='white')
    mp.plot_values(df['lon'].values,
                   df['lat'].values,
                   df['val'].values, textsize=12, labelbuffer=5, color='k')
    mp.drawcounties()
    mp.postprocess(filename='test.png')
    mp.close()


if __name__ == '__main__':
    main()
