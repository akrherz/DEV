"""Fix damage from akrherz/pyIEM#442"""

# stdlib
import datetime

import pandas as pd

# Third Party
from psycopg2.extras import RealDictCursor
from pyiem.nws.products.pirep import Pirep
from pyiem.util import get_dbconn, logger, utc
from pywwa.workflows.pirep import LOCS, load_locs

LOG = logger()


def do(pgconn, date):
    """do a date."""
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    sts = utc(date.year, date.month, date.day)
    cursor.execute(
        "SELECT ctid, st_x(geom::geometry), st_y(geom::geometry), report "
        "from pireps WHERE valid >= %s and valid < %s",
        (sts, sts + datetime.timedelta(days=1)),
    )
    updates = 0
    for row in cursor:
        fake = "000 \r\r\nSAUS99 KDMX 241200\r\r\n%s=\r\r\n" % (row[3],)
        p = Pirep(fake, nwsli_provider=LOCS)
        if not p.reports:
            print(fake)
            continue
        newlon = p.reports[0].longitude
        newlat = p.reports[0].latitude
        if newlon is None:
            print(fake)
            continue
        dist = ((newlon - row[1]) ** 2 + (newlat - row[2]) ** 2) ** 0.5
        if dist < 0.0001:
            continue
        cursor2.execute(
            "UPDATE pireps SET geom = 'SRID=4326;POINT(%s %s)' "
            "WHERE ctid = %s",
            (newlon, newlat, row[0]),
        )
        updates += 1

    print("%s updated %s/%s rows" % (date, updates, cursor.rowcount))
    cursor2.close()
    pgconn.commit()


def main():
    """GO Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=RealDictCursor)
    load_locs(cursor)
    cursor.close()
    for date in pd.date_range("2015/01/19", "2021/04/22"):
        do(pgconn, date)


if __name__ == "__main__":
    print("hi")
    main()
