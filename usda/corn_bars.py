"""Cloropleth of progress."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mpcolors
import datetime
from matplotlib.colors import rgb2hex
import matplotlib.patheffects as PathEffects
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def get_data():
    """The data we want and the data we need"""
    pgconn = get_dbconn('coop')
    df = read_sql("""
        select year, week_ending, num_value, state_alpha from nass_quickstats
        where commodity_desc = 'CORN' and statisticcat_desc = 'PROGRESS'
        and unit_desc = 'PCT PLANTED' and state_alpha = 'IA' and
        util_practice_desc = 'ALL UTILIZATION PRACTICES'
        and num_value is not null
        ORDER by state_alpha, week_ending
    """, pgconn, index_col=None)
    df['week_ending'] = pd.to_datetime(df['week_ending'])
    df['doy'] = pd.to_numeric(df['week_ending'].dt.strftime("%j"))
    df = df.set_index('week_ending')
    df['delta'] = df.groupby('year')['num_value'].diff()
    return df


def main():
    """Go Main Go"""
    df = get_data()

    cmap = plt.get_cmap('jet')
    cmap.set_over('black')
    cmap.set_under('white')
    bins = np.arange(0, 71, 10)
    bins[0] = 0.01
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    (fig, ax) = plt.subplots(1, 1, figsize=(6.4, 6.4))

    yearmax = df[['year', 'delta']].groupby('year').max()
    for year, df2 in df.groupby('year'):
        for _, row in df2.iterrows():
            ax.bar(
                row['doy'], 1, bottom=year-0.5, width=7, ec='None',
                fc=cmap(norm([row['delta']]))[0])

    sts = datetime.datetime(2000, 3, 22)
    ets = datetime.datetime(2000, 6, 25)
    now = sts
    interval = datetime.timedelta(days=1)
    jdays = []
    labels = []
    while now < ets:
        if now.day in [1, 8, 15, 22]:
            fmt = "%-d\n%b" if now.day == 1 else "%-d"
            jdays.append(int(now.strftime("%j")))
            labels.append(now.strftime(fmt))
        now += interval

    ax.set_xticks(jdays)
    ax.set_xticklabels(labels)

    ax.set_yticks(range(1979, 2020))
    ylabels = []
    for yr in range(1979, 2020):
        if yr % 5 == 0:
            ylabels.append("%s %.0f" % (yr, yearmax.at[yr, 'delta']))
        else:
            ylabels.append("%.0f" % (yearmax.at[yr, 'delta'],))
    ax.set_yticklabels(ylabels, fontsize=10)

    ax.set_ylim(1978.5, 2019.5)
    ax.set_xlim(min(jdays), max(jdays))
    ax.grid(linestyle='-', linewidth='0.5', color='#EEEEEE', alpha=0.7)
    ax.set_title((
        "USDA NASS Weekly Corn Planting Progress, till 2 June 2019\n"
        "Iowa % acres planted over weekly periods, "
        "yearly max labelled at side"))

    ax2 = plt.axes(
        [0.92, 0.1, 0.07, 0.8], frameon=False, yticks=[], xticks=[])
    colors = []
    for i in range(len(bins)):
        colors.append(rgb2hex(cmap(i)))
        txt = ax2.text(
            0.5, i - 0.5, "%.0f" % (bins[i],), ha='center', va='center',
            color='w')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="k")])
    ax2.barh(np.arange(len(bins)), [1]*len(bins), height=1,
             color=cmap(norm(bins)),
             ec='None')

    fig.savefig('test.png')


if __name__ == '__main__':
    main()
