"""List out close proximity NLDN strikes."""
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, utc


def process(network, station, sts, ets):
    """Make the magic happen."""
    nt = NetworkTable(network)
    pgconn = get_dbconn("nldn")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        select st_x(geom), st_y(geom), valid,
        st_distance(geography(geom),
                    geography(ST_GeometryFromText('SRID=4326;POINT(%s %s)')))
        from nldn_all WHERE
        valid between %s and %s and
        st_distance(geom, ST_GeometryFromText('SRID=4326;POINT(%s %s)')) < 0.2
        ORDER by valid ASC
    """,
        (
            nt.sts[station]["lon"],
            nt.sts[station]["lat"],
            sts,
            ets,
            nt.sts[station]["lon"],
            nt.sts[station]["lat"],
        ),
    )
    stamp = ""
    fn = "%s_%s_%s.csv" % (
        station,
        sts.strftime("%Y%m%d%H"),
        ets.strftime("%Y%m%d%H"),
    )
    with open(fn, "w") as fh:
        fh.write("SID,UTCVALID,LON,LAT,DISTANCE_KM\n")
        for row in cursor:
            if stamp != row[2].strftime("%Y%m%d%H%M%S"):
                fh.write(
                    ("%s,%s,%6.3f,%6.3f,%6.3f\n")
                    % (
                        station,
                        row[2].strftime("%d %b %Y %H:%M:%S"),
                        row[0],
                        row[1],
                        row[3] / 1000.0,
                    )
                )
            stamp = row[2].strftime("%Y%m%d%H%M%S")


def main(argv):
    """Go Main Go"""
    network = argv[1]
    station = argv[2]
    process(network, station, utc(2018, 6, 1), utc(2019, 11, 6))


if __name__ == "__main__":
    main(sys.argv)
