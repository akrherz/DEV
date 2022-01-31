"""Write a hacky counties file, because this is my life."""

from pyiem.util import get_dbconn
import numpy as np


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    with open("counties.csv", "w", encoding="utf-8") as fp:
        fp.write("State,County,long,lat\n")
        for lon in np.arange(-104, -80, 0.125):
            for lat in np.arange(36, 50, 0.125):
                cursor.execute(
                    """
                    SELECT state, name from ugcs where end_ts is null
                    and ST_Contains(
                        geom, ST_SetSRID(
                            ST_GeomFromText('POINT(%s %s)'), 4326))
                    and substr(ugc, 3, 1) = 'C'
                """,
                    (lon, lat),
                )
                if cursor.rowcount == 0:
                    continue
                (state, county) = cursor.fetchone()

                fp.write(
                    "%s,%s,%.4f,%.4f\n"
                    % (state.lower(), county.lower(), lon, lat)
                )


if __name__ == "__main__":
    main()
