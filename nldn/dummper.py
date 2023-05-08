"""List out close proximity NLDN strikes."""
import sys

from tqdm import tqdm

from pyiem.util import get_dbconn


def process(lon, lat, distkm, fh, year, month):
    """Make the magic happen."""
    pgconn = get_dbconn("nldn")
    cursor = pgconn.cursor()
    cursor.execute(
        f"""
        select st_x(geom), st_y(geom), valid at time zone 'UTC',
        st_distance(geography(geom),
                    geography(ST_GeometryFromText('SRID=4326;POINT(%s %s)'))),
        signal, multiplicity, axis, eccentricity, ellipse, chisqr
        from nldn{year}_{month:02d} WHERE
        ST_DWithin(
            geography(geom),
            geography(ST_GeometryFromText('SRID=4326;POINT(%s %s)')),
            %s * 1000.)
        ORDER by valid ASC
    """,
        (
            lon,
            lat,
            lon,
            lat,
            distkm,
        ),
    )
    for row in cursor:
        fh.write(
            ("%s,%6.4f,%6.4f,%6.4f,%s,%s,%s,%s,%s,%s\n")
            % (
                row[2].strftime("%d %b %Y %H:%M:%S.%f"),
                row[0],
                row[1],
                row[3] / 1000.0,
                *row[4:],
            )
        )


def main(argv):
    """Go Main Go"""
    lon = float(argv[1])
    lat = float(argv[2])
    distkm = 250
    fn = "%sW_%sN__%skm_20170101_20210101.csv" % (
        0 - lon,
        lat,
        distkm,
    )
    with open(fn, "w") as fh:
        fh.write(
            "UTCVALID,LON,LAT,DISTANCE_KM,SIGNAL,MULTIPLICITY,AXIS,"
            "ECCENTRICITY,ELLIPSE,CHISQR\n"
        )
        progress = tqdm(range(2017, 2021))
        for year in progress:
            progress.set_description(str(year))
            for month in range(1, 13):
                process(lon, lat, distkm, fh, year, month)


if __name__ == "__main__":
    main(sys.argv)
