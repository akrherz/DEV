"""List out close proximity NLDN strikes"""

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, utc


def process(station, sts, ets):
    nt = NetworkTable("IA_RWIS")
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()
    cursor.execute("""
    select st_x(geom), st_y(geom), valid,
    st_distance(geography(geom),
                geography(ST_GeometryFromText('SRID=4326;POINT(%s %s)')))
    from nldn_all WHERE
    valid between %s and %s and
    st_distance(geom, ST_GeometryFromText('SRID=4326;POINT(%s %s)')) < 0.2
    ORDER by valid ASC
    """, (nt.sts[station]['lon'], nt.sts[station]['lat'],
          sts, ets, nt.sts[station]['lon'], nt.sts[station]['lat']))
    stamp = ""
    for row in cursor:
        if stamp != row[2].strftime("%Y%m%d%H%M%S"):
            print(("%s %s %6.3f %6.3f %6.3f"
                   ) % (station, row[2].strftime("%d %b %Y %H:%M:%S"), row[0],
                        row[1], row[3] / 1000.))
        stamp = row[2].strftime("%Y%m%d%H%M%S")


def main():
    """Go Main Go"""
    # RSDI4 1-2z 12 Jun 2018
    process('RSDI4', utc(2018, 6, 12, 1), utc(2018, 6, 12, 2))
    # RGAI4 5-9z 11 Jun 2018
    process('RGAI4', utc(2018, 6, 11, 5), utc(2018, 6, 11, 9))
    # VCTI4 17-19z 26 May 2018
    process('VCTI4', utc(2018, 5, 26, 19), utc(2018, 5, 26, 21))


if __name__ == '__main__':
    main()
