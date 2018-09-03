"""The 30 minute shot clock."""
import datetime

import pytz
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt


def get_data():
    """Fetch."""
    pgconn = get_dbconn('postgis')
    df = read_sql("""
        select distinct date_trunc('minute', valid) as dt from
        nldn2018_09 where valid > '2018-09-01 17:00'
        and st_distance(
            ST_GeomFromEWKT('SRID=4326;POINT(-93.6379 42.0140)')::geography,
            geom::geography) < 12874.8 ORDER by dt ASC
    """, pgconn, index_col=None)
    df.to_csv('data.csv')


def main():
    """Go Main Go."""
    # get_data()
    df = pd.read_csv('data.csv')
    df['dt'] = pd.to_datetime(df['dt']) - datetime.timedelta(hours=5)
    df['s'] = df['dt'].dt.strftime("%Y%m%d%H%M")
    x = []
    y = []
    sts = datetime.datetime(2018, 9, 1, 19)
    ets = datetime.datetime(2018, 9, 2, 2, 1)
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
    ax.plot(x, y)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_yticks(list(range(0,91, 15)))
    ax.set_ylabel("Minutes since Last Lightning Strike")
    ax.set_xlabel("Evening of 1 September 2018 (CDT)")
    ax.axhline(30, lw=2, color='r')
    ax.grid(True)
    ax.set_title((
        "Iowa State vs South Dakota State Football Game\n"
        "Time since Last Lightning Strike within 8 miles of Jack Trice Stadium\n"
        "Data courtesy of National Lightning Detection Network"))
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
