"""Compute water-yearly VPD"""

from __future__ import print_function

import metpy.calc as mcalc
from metpy.units import units
from pandas.io.sql import read_sql
from pyiem.datatypes import temperature
from pyiem.util import get_dbconn
from pyiem import meteorology


def main():
    """Go Main Go"""
    pgconn = get_dbconn('scan')
    for station in ['S2004', 'S2196', 'S2002', 'S2072', 'S2068',
                    'S2031', 'S2001', 'S2047']:
        df = read_sql("""
        select extract(year from valid + '2 months'::interval) as wy,
        tmpf, dwpf from alldata where station = %s and tmpf is not null
        and dwpf is not null
        """, pgconn, params=(station, ), index_col=None)
        df['mixingratio'] = meteorology.mixing_ratio(
            temperature(df['dwpf'].values, 'F')).value('KG/KG')
        df['vapor_pressure'] = mcalc.vapor_pressure(
            1000. * units.mbar,
            df['mixingratio'].values * units('kg/kg')).to(units('kPa'))
        df['saturation_mixingratio'] = (
            meteorology.mixing_ratio(
                temperature(df['tmpf'].values, 'F')).value('KG/KG'))
        df['saturation_vapor_pressure'] = mcalc.vapor_pressure(
            1000. * units.mbar,
            df['saturation_mixingratio'].values * units('kg/kg')).to(units('kPa'))
        df['vpd'] = df['saturation_vapor_pressure'] - df['vapor_pressure']
        means = df.groupby('wy').mean()
        counts = df.groupby('wy').count()
        for yr, row in means.iterrows():
            print(("%s,%s,%.0f,%.3f"
                   ) % (yr, station, counts.at[yr, 'vpd'], row['vpd']))


if __name__ == '__main__':
    main()
