"""VPD"""
from __future__ import print_function
import datetime

from pyiem.util import get_dbconn
from pyiem.datatypes import temperature
from pyiem import meteorology
from metpy.units import units
import metpy.calc as mcalc
import pandas as pd
from pandas.io.sql import read_sql


def main():
    """Go Main Go"""
    pgconn = get_dbconn('asos', user='nobody')
    daily = read_sql("""
        SELECT date(valid), max(tmpf) as high, min(tmpf) as low from alldata
        where station = 'DSM' and tmpf between -50 and 120 GROUP by date
    """, pgconn, index_col='date')

    daily['mixingratio'] = meteorology.mixing_ratio(
        temperature(daily['low'].values, 'F')).value('KG/KG')
    daily['vapor_pressure'] = mcalc.vapor_pressure(
        1000. * units.mbar,
        daily['mixingratio'].values * units('kg/kg')).to(units('kPa'))
    daily['saturation_mixingratio'] = (
        meteorology.mixing_ratio(
            temperature(daily['high'].values, 'F')).value('KG/KG'))
    daily['saturation_vapor_pressure'] = mcalc.vapor_pressure(
        1000. * units.mbar,
        daily['saturation_mixingratio'].values * units('kg/kg')
        ).to(units('kPa'))
    daily['vpd'] = daily['saturation_vapor_pressure'] - daily['vapor_pressure']

    df = read_sql("""
    SELECT valid at time zone 'UTC' as valid, tmpf, dwpf
    from alldata where station = 'DSM'
    and tmpf >= dwpf and tmpf between -50 and 120
    and extract(hour from valid) between 8 and 16
    """, pgconn, index_col=None)
    df['valid'] = pd.to_datetime(df['valid']) + datetime.timedelta(hours=6)
    df.set_index('valid', inplace=True)
    print(df.index)

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

    rows = []
    for date, gdf in df.groupby(df.index.date):
        if date not in daily.index:
            continue
        if date.month == 7:
            print("%s %.3f %.3f" % (date, daily.at[date, 'vpd'],
                                    gdf['vpd'].max()))
            rows.append(dict(date=date, daily=daily.at[date, 'vpd'],
                             hourly=gdf['vpd'].max()))

    res = pd.DataFrame(rows)
    res['date'] = pd.to_datetime(res['date'])
    res.set_index('date', inplace=True)
    yearly = res.groupby(res.index.year).mean()
    yearly.to_csv('yearly.csv')


if __name__ == '__main__':
    main()
