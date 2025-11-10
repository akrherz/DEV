"""
Specialized airspaces entry for Alaska AAWU zones

"""

import geopandas as gpd
from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    df = gpd.read_file("https://www.weather.gov/source/aawu/AAWU_airmets.json")
    conn = get_dbconn("postgis")
    cursor = conn.cursor()
    cursor.execute("DELETE from airspaces where type_code = 'AKZONE'")
    if cursor.rowcount > 0:
        LOG.info("Removed dbrow for %s", cursor.rowcount)
    for row in df.itertuples():
        # They store lon as 0-360
        cursor.execute(
            """
            INSERT into airspaces(ident, type_code, name, geom) values
            (%s, 'AKZONE', %s,
            ST_Multi(ST_ShiftLongitude(ST_GeomFromText(%s, 4326))))
            """,
            (row.id, row.name, row.geometry.buffer(0).wkt),
        )
    cursor.close()
    conn.commit()


if __name__ == "__main__":
    main()
