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
        SELECT station, snow_jul1 - snow_jul1_normal as s
        from cli_data where valid = '2018-01-24' and snow_jul1 > 0
        and snow_jul1_normal > 0)

    select station, st_x(geom), st_y(geom), c.s from
    data c JOIN stations s on (s.id = c.station)
    WHERE s.network = 'NWSCLI'
    """)

    lats = []
    lons = []
    colors = []
    vals = []

    for row in cursor:
        lats.append(row[2])
        lons.append(row[1])
        vals.append(row[3])
        colors.append('#ff0000' if row[3] < 0 else '#0000ff')

    mp = MapPlot(sector='midwest', axisbg='white',
                 title=("2017-2018 Snowfall Total Departure "
                        "from Average [inches]"),
                 subtitle='25 Jan 2018 Based on NWS CLI Reporting Sites')
    mp.plot_values(lons, lats, vals, fmt='%s', textsize=12, color=colors,
                   labelbuffer=1)
    mp.postprocess(filename='test.png')


if __name__ == '__main__':
    main()
