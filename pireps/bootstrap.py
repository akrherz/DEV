"""
Create airspaces folder
"""

import requests

import geopandas as gpd
from pyiem.util import get_dbconn, logger
from shapely import force_2d

LOG = logger()
URL = (
    "https://opendata.arcgis.com/api/v3/datasets/"
    "67885972e4e940b2aa6d74024901c561_0/downloads/data?"
    "format=geojson&spatialRefId=4326&where=1%3D1"
)


def main():
    """Go Main Go."""
    df = gpd.GeoDataFrame.from_features(requests.get(URL, timeout=30).json())
    conn = get_dbconn("postgis")
    cursor = conn.cursor()
    cursor.execute(
        "DELETE from airspaces where type_code in %s",
        (tuple(df["TYPE_CODE"].unique()),),
    )
    LOG.info("Removed %s airspace rows", cursor.rowcount)
    # Data source has upper/lower, creating dups
    dedup = []
    for row in df.itertuples():
        geo = row.geometry
        if not geo.is_valid:
            geo = row.geometry.buffer(0)
        if row.TYPE_CODE == "ARTCC" and row.LEVEL_ == "U":
            continue
        key = f"{row.IDENT}_{row.TYPE_CODE}_{geo.area:.4f}"
        if key in dedup:
            continue
        dedup.append(key)
        cursor.execute(
            """
            INSERT into airspaces(ident, type_code, name, geom)
            VALUES(%s, %s, %s, ST_Multi(ST_GeomFromText(%s, 4326)))
            """,
            (row.IDENT, row.TYPE_CODE, row.NAME, force_2d(geo).wkt),
        )
    LOG.info("Ins %s rows (%s dup)", len(dedup), len(df.index) - len(dedup))
    cursor.close()
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
