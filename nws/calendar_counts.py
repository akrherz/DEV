"""ex"""
import datetime

from pyiem.plot import calendar_plot
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()
    cursor.execute("""
    WITH data as (
    SELECT eventid, min(issue) from warnings_2017 where wfo = 'OUN' and
    phenomena = 'FG' and significance = 'Y' GROUP by eventid
    )

    SELECT date(min), count(*) from data GROUP by date
    """)
    data = {}
    for row in cursor:
        data[row[0]] = {'val': row[1]}
    fig = calendar_plot(datetime.date(2017, 1, 1),
                        datetime.date(2017, 12, 31), data, heatmap=True)
    fig.text(0.5, 0.95, "2017 OUN Daily Severe Thunderstorm Warnings",
             ha='center', fontsize=20)
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
