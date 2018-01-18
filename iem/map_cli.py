"""Map cli_data"""
from __future__ import print_function
import datetime

from pyiem.util import get_dbconn
from pyiem.plot import MapPlot


def main():
    """Map some CLI data"""
    pgconn = get_dbconn('iem')
    cursor = pgconn.cursor()

    cursor.execute("""
    WITH data as (
        SELECT station, valid,
        snow + lag(snow) OVER (PARTITION by station ORDER by valid ASC) as s
        from cli_data)

    select station, st_x(geom), st_y(geom),
    max(case when c.s >= 3 then valid else '1990-01-01'::date end),
    max(case when c.s > 0 then valid else '1990-01-01'::date end) from
    data c JOIN stations s on (s.id = c.station)
    WHERE s.network = 'NWSCLI'
    GROUP by station, st_x, st_y
    """)

    lats = []
    lons = []
    colors = []
    vals = []

    base = datetime.date.today()

    for row in cursor:
        if row[4].year < 2017:
            # print(row)
            continue
        lats.append(row[2])
        lons.append(row[1])
        days = (base - row[3]).days
        if days > 10000:
            print(row)
            continue
        vals.append(days)
        colors.append('#ff0000' if days > 1000 else '#0000ff')

    mp = MapPlot(sector='midwest', axisbg='white',
                 title="Days since last Two Day Snowfall of 3+ Inches",
                 subtitle='17 Jan 2017 based on NWS issued CLI Reports')
    mp.plot_values(lons, lats, vals, fmt='%s', textsize=12, color=colors,
                   labelbuffer=1)
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
