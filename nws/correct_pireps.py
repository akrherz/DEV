"""Fix damage from akrherz/pyIEM#108"""

from pyiem.nws.products.pirep import OV_LATLON
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute("""
        SELECT oid, st_x(geom::geometry), st_y(geom::geometry), report
        from pireps
    """)
    updates = 0
    for row in cursor:
        for token in row[3].split("/"):
            if not token.startswith("OV "):
                continue
            m = OV_LATLON.match(token[2:])
            if not m:
                continue
            d = m.groupdict()
            lat = float("%s.%i" % (
                d['lat'][:-2],
                int(float(d['lat'][-2:]) / 60. * 10000.)))
            if d['latsign'] == 'S':
                lat = 0 - lat
            lon = float("%s.%i" % (
                d['lon'][:-2],
                int(float(d['lon'][-2:]) / 60. * 10000.)))
            if d['lonsign'] == 'W':
                lon = 0 - lon
            if abs(lon - row[1]) > 0.01 or abs(lat - row[2]) > 0.01:
                print(
                    "Update! %s %.2f -> %.2f %.2f -> %.2f" % (
                        token, row[2], lat, row[1], lon
                    ))
                cursor2.execute("""
                    UPDATE pireps SET geom = 'SRID=4326;POINT(%s %s)'
                    WHERE oid = %s
                """, (lon, lat, row[0]))
                updates += 1

    print("updated %s/%s rows" % (updates, cursor.rowcount))
    cursor2.close()
    pgconn.commit()


if __name__ == '__main__':
    main()
