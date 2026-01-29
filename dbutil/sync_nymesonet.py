"""Build out NY Mesonet table."""

import geopandas as gpd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.util import convert_value
from sqlalchemy.engine import Connection

SRC = (
    "https://hub.arcgis.com/api/v3/datasets/"
    "3a68bbb9003a4f1e91fd5af64c3bf1a5_0/downloads/data?"
    "format=geojson&spatialRefId=4326&where=1%3D1"
)


@with_sqlalchemy_conn("mesosite")
def main(conn: Connection | None = None):
    """Go Main Go."""
    stationsdf = gpd.read_file(SRC)
    for _, row in stationsdf.iterrows():
        # As found in SHEF source
        sid = f"NYSM{row['code']}"
        res = conn.execute(
            sql_helper(
                "select * from stations where id = :sid and network = 'NY_DCP'"
            ),
            {"sid": sid},
        )
        if res.rowcount == 1:
            continue
        # Add!
        print(f"Adding {sid}")
        elev = convert_value(row["Elev"], "ft", "m")
        conn.execute(
            sql_helper(
                """
            INSERT INTO stations (id, network, name, state, country,
            plot_name, elevation, geom, online, metasite) VALUES (
            :sid, 'NY_DCP', :name, 'NY', 'US',
            :name, :elev, ST_Point(:lon, :lat, 4326), 't', 'f'
            )
            """
            ),
            {
                "sid": sid,
                "name": f"{row['station_na']} NY Mesonet",
                "elev": elev,
                "lat": row["lat"],
                "lon": row["lon"],
            },
        )
    conn.commit()


if __name__ == "__main__":
    main()
