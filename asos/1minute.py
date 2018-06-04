"""Plot of 1minute ASOS data"""
import datetime

import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
from pyiem.datatypes import speed, pressure


def main():
    """Go Main"""
    pgconn = get_dbconn('asos')
    df = read_sql("""
    SELECT valid, tmpf, drct, sknt, gust_sknt, pres1 from t2018_1minute
    where station = %s and valid >= '2018-06-02 07:30' and
    valid <= '2018-06-02 09:15' ORDER by valid ASC
    """, pgconn, params=('MCW', ), index_col='valid')
    xticks = []
    xticklabels = []
    for valid in df.index.values:
        if pd.to_datetime(valid).minute % 15 == 0:
            xticks.append(valid)
            ts = pd.to_datetime(valid) - datetime.timedelta(hours=5)
            xticklabels.append(ts.strftime("%-H:%M\n%p"))

    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.15, 0.75, 0.7])

    ax.bar(df.index.values, speed(df['gust_sknt'], 'KT').value('MPH'),
           width=1/1440., color='red')
    ax.bar(df.index.values, speed(df['sknt'], 'KT').value('MPH'),
           width=1/1440., color='tan')
    ax.set_ylabel("Wind Speed (tan) & Gust (red) [mph]")
    ax.grid(True, zorder=5)
    ax.set_ylim(0, 60)
    ax.set_title(("Mason City, IA (KMCW) ASOS 1 Minute Interval Data for 2 Jun 2018\n"
                  "Wind Speed, Wind Gust and Air Pressure for Wake Low Event"))

    ax2 = ax.twinx()
    ax2.plot(df.index.values, pressure(df['pres1'], 'IN').value('MB'),
             color='g', lw=2)
    ax2.set_ylabel("Air Pressure [hPa]", color='green')
    ax2.set_xticks(xticks)
    ax2.set_xticklabels(xticklabels)
    ax.set_xlabel("2 June 2018 CDT")
    ax2.set_ylim(960, 972)
    ax2.set_yticks(range(960, 974, 2))
    # ax2.set_zorder(ax.get_zorder()-1)
    # ax2.set_ylim(0, 360)
    # ax2.set_yticks(range(0, 361, 45))
    # ax2.set_yticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])

    fig.savefig('test.png')


if __name__ == '__main__':
    main()
