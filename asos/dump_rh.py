"""Dump RH frequencies per year."""

from metpy.units import units
from metpy.calc import relative_humidity_from_dewpoint
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn('asos')
    df = read_sql("""
        SELECT date_trunc('hour', valid) as ts, avg(tmpf) as temp,
        avg(dwpf) as dew from alldata where station = 'DSM'
        and extract(month from valid) in (5, 6, 7, 8) and tmpf is not null
        and dwpf is not null GROUP by ts
    """, pgconn, index_col=None)
    df['relh'] = relative_humidity_from_dewpoint(
        df['temp'].values * units('degF'),
        df['dew'].values * units('degF')
    ) * 100.
    df['year'] = df['ts'].dt.year
    counts = df[['year', 'relh']].groupby('year').count()
    df2 = df[df['relh'] >= 87.]
    counts2 = df2[['year', 'relh']].groupby('year').count()
    counts['hits'] = counts2['relh']
    counts['freq'] = counts['hits'] / counts['relh']
    counts.to_csv('test.csv')


if __name__ == '__main__':
    main()