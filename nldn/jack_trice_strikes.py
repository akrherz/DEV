"""The 30 minute shot clock."""
import datetime

import pytz
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt


def get_data():
    """Fetch."""
    pgconn = get_dbconn('nldn')
    df = read_sql("""
        select distinct date_trunc('minute', valid) as dt from
        nldn2019_09 where valid > '2019-09-14 15:00' and
        valid < '2019-09-14 21:00' and st_distance(
            ST_GeomFromEWKT('SRID=4326;POINT(-93.6379 42.0140)')::geography,
            geom::geography) < 12874.8 ORDER by dt ASC
    """, pgconn, index_col=None)
    df.to_csv('data.csv')


def main():
    """Go Main Go."""
    get_data()
    df = pd.read_csv('data.csv')
    df['dt'] = pd.to_datetime(df['dt']) - datetime.timedelta(hours=5)
    df['s'] = df['dt'].dt.strftime("%Y%m%d%H%M")
    x = []
    y = []
    sts = datetime.datetime(2019, 9, 14, 15)
    ets = datetime.datetime(2019, 9, 14, 21)
    interval = datetime.timedelta(minutes=1)
    now = sts
    current = None
    xticks = []
    xticklabels = []
    while now < ets:
        if now.minute == 0:
            xticks.append(now)
            xticklabels.append(now.strftime("%-I %p"))
        x.append(now)
        if now.strftime("%Y%m%d%H%M") in df['s'].values:
            current = 0
        else:
            if current is not None:
                current += 1
        y.append(current)
        now += interval

    (fig, ax) = plt.subplots(1, 1)
    ax.plot(x, y, zorder=6)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_yticks(list(range(0, 91, 15)))
    ax.set_ylabel(
        "Minutes since Last Lightning Strike")
    ax.set_xlabel(
        "Evening of 14 September 2019 (CDT), approximate game delays shaded")
    ax.axhline(30, lw=2, color='r')
    ax.set_ylim(bottom=-0.1)
    ax.axvspan(
        datetime.datetime(2019, 9, 14, 15, 29),
        datetime.datetime(2019, 9, 14, 16, 18), color='k', alpha=0.4, zorder=2)
    ax.axvspan(
        datetime.datetime(2019, 9, 14, 16, 45),
        datetime.datetime(2019, 9, 14, 18, 52), color='k', alpha=0.4, zorder=2)
    ax.grid(True)
    ax.set_title((
        "Iowa State vs Iowa Football Game\n"
        "Time since Last Lightning Strike within 8 miles of Jack Trice Stadium\n"
        "Data courtesy of National Lightning Detection Network"))
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
