"""Here lies the script that makes bot warnings

Take the Time Motion Location and create a MOS style polygon
"""

import math
import sys

import psycopg2.extras
import pyproj
from pyiem.util import get_dbconn
from tqdm import tqdm

P2163 = pyproj.Proj(init="epsg:2163")


def dir2ccwrot(mydir):
    """Convert to CCW"""
    res = None
    if mydir >= 270 and mydir <= 360:
        res = 0 - (mydir - 270)
    elif mydir >= 180:
        res = 270 - mydir
    elif mydir >= 90:
        res = 180 - (mydir - 90)
    elif mydir >= 0:
        res = 180 + (90 - mydir)
    return res


def main(argv):
    """Go main Go"""
    postgis = get_dbconn("postgis")
    pcursor = postgis.cursor(cursor_factory=psycopg2.extras.DictCursor)
    pcursor2 = postgis.cursor()

    pcursor2.execute("DELETE from bot_warnings where wfo = %s", (argv[1],))
    print(
        ("Removed %s rows for WFO: %s in bot_warnings")
        % (pcursor2.rowcount, argv[1])
    )

    pcursor.execute(
        """
        SELECT issue, init_expire, tml_direction, tml_sknt,
        ST_x(tml_geom) as tml_lon, ST_y(tml_geom) as tml_lat, wfo,
        phenomena, significance, eventid from sbw WHERE
        phenomena = 'TO' and status = 'NEW' and wfo = %s
        and issue between '2008-01-01' and '2020-01-01'
        """,
        (argv[1],),
    )
    for row in tqdm(pcursor, total=pcursor.rowcount):
        issue = row["issue"]
        expire = row["init_expire"]
        tml_direction = row["tml_direction"]
        tml_sknt = float(row["tml_sknt"])
        # Slow moving storms are trouble
        if tml_sknt < 5:
            tml_sknt = 5
        lat = row["tml_lat"]
        lon = row["tml_lon"]
        if lat is None:
            continue
        xtml, ytml = P2163(lon, lat)
        smps = float(tml_sknt) * 0.514
        # This is the from angle, need to rotate 180 to get the to angle
        angle = dir2ccwrot(tml_direction)
        rad = math.radians(angle)
        # print("%s %s %s" % (tml_direction, angle, rad))

        xtml2 = xtml + math.cos(rad) * smps * 1800.0  # 30 min
        ytml2 = ytml + math.sin(rad) * smps * 1800.0  # 30 min
        ulx = xtml + math.cos(rad + math.pi / 2.0) * 10000.0
        uly = ytml + math.sin(rad + math.pi / 2.0) * 10000.0  # 10km "north"
        llx = xtml - math.cos(rad + math.pi / 2.0) * 10000.0
        lly = ytml - math.sin(rad + math.pi / 2.0) * 10000.0  # 10km "south"
        urx = xtml2 + math.cos(rad + math.pi / 2.0) * 10000.0
        ury = ytml2 + math.sin(rad + math.pi / 2.0) * 10000.0  # 10km "north"
        lrx = xtml2 - math.cos(rad + math.pi / 2.0) * 30000.0
        lry = ytml2 - math.sin(rad + math.pi / 2.0) * 30000.0  # 30km "south"

        # Create the warning
        sql = """
        INSERT into bot_warnings(issue, expire, gtype, wfo,
        geom, eventid, phenomena, significance, status) VALUES ('%s', '%s',
        'P', '%s',
        ST_Transform(ST_GeomFromText('SRID=2163;MULTIPOLYGON(((%s %s, %s %s,
        %s %s, %s %s, %s %s)))'),4326),
        %s, '%s', '%s', 'NEW')
        """ % (
            issue,
            expire,
            row["wfo"],
            llx,
            lly,
            ulx,
            uly,
            urx,
            ury,
            lrx,
            lry,
            llx,
            lly,
            row["eventid"],
            row["phenomena"],
            row["significance"],
        )
        # print(sql)
        pcursor2.execute(sql)

    pcursor2.close()
    postgis.commit()


if __name__ == "__main__":
    main(sys.argv)
