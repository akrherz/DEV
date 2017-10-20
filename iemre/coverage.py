import calendar

import netCDF4
import pandas as pd
import numpy as np
import tqdm
import matplotlib.pyplot as plt


def get_data():
    """Get data"""
    nc = netCDF4.Dataset('/mesonet/data/iemre/state_weights.nc')
    iowa = nc.variables['IA'][:]
    # totalpts = np.sum(iowa > 0)
    nc.close()

    rows = []
    for year in tqdm.tqdm(range(1893, 2018)):
        nc = netCDF4.Dataset('/mesonet/data/iemre/'+str(year)+'_mw_daily.nc')
        high = nc.variables['low_tmpk_12z']
        minval = high[200]
        for idx in range(201, 360):
            minval = np.minimum(minval, high[idx])
            rows.append(dict(year=year, doy=idx,
                             count=np.sum(
                                 np.logical_and(minval < 273, iowa > 0))))

        nc.close()

    df = pd.DataFrame(rows)
    df.to_csv('tmp.csv')


def main():
    """go"""
    df = pd.read_csv('tmp.csv')
    iowapts = df['count'].max()
    df['areal'] = df['count'] / iowapts * 100.
    (fig, ax) = plt.subplots(1, 1)
    df2 = df.groupby('doy').mean()
    ax.plot(df2.index.values, df2['areal'].values, label='Average', lw=2)
    df2 = df.groupby('doy').max()
    ax.plot(df2.index.values, df2['areal'].values, label='Max', lw=2)
    df2 = df.groupby('doy').min()
    ax.plot(df2.index.values, df2['areal'].values, label='Min', lw=2)
    df2 = df[df['year'] == 2016]
    ax.plot(df2['doy'].values, df2['areal'].values, label='2016', lw=2)
    df2 = df[df['year'] == 2017]
    ax.plot(df2['doy'].values, df2['areal'].values, label='2017', lw=2)
    ax.grid(True)
    ax.legend(loc=2)
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(235, 336)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_ylabel("Areal Coverage [%]")
    ax.set_title(r"Iowa Areal Coverage of First Fall sub 32$^\circ$F")
    fig.savefig('171020.png')


if __name__ == '__main__':
    main()
