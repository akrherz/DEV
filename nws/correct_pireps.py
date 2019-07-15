"""Fix damage from akrherz/pyIEM#108"""

from pyiem.nws.products.pirep import Pirep
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute("""
        SELECT oid, st_x(geom::geometry), st_y(geom::geometry), report
        from pireps WHERE report ~* 'OV TED'
    """)
    updates = 0
    nwsli_provider = {
        'TED': {'lat': 61.17, 'lon': -149.99},
        'PANC': {'lat': 61.17, 'lon': -149.99},
        'ANC': {'lat': 61.17, 'lon': -149.99},
    }
    for row in cursor:
        fake = "000 \r\r\nSAUS99 KDMX 241200\r\r\n%s=\r\r\n" % (row[3], )
        p = Pirep(fake, nwsli_provider=nwsli_provider)
        if not p.reports:
            print(fake)
            continue
        cursor2.execute("""
            UPDATE pireps SET geom = 'SRID=4326;POINT(%s %s)'
            WHERE oid = %s
        """, (p.reports[0].longitude, p.reports[0].latitude, row[0]))
        updates += 1

    print("updated %s/%s rows" % (updates, cursor.rowcount))
    cursor2.close()
    pgconn.commit()


if __name__ == '__main__':
    main()
