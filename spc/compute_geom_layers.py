"""
Backfill the archive with computed geom + geom_layers columns

see akrherz/pyIEM#738

NOTE: Some manual work was done to rectify the ERO archive as it contained a
mix of layered vs cookie cutter geometries.
"""

import sys

import geopandas as gpd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.nws.products.spcpts import THRESHOLD_ORDER
from shapely.geometry import MultiPolygon


def do(product_id):
    """Do the magic :/"""
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            """
            select * from spc_outlooks where product_id = %s and
            geom is not null
            """,
            conn,
            params=(product_id,),
            geom_col="geom_layers",
        )
    if df.empty:
        return
    for idx, row in df.iterrows():
        val = 1000
        if row["threshold"] in THRESHOLD_ORDER:
            val = THRESHOLD_ORDER.index(row["threshold"])
        df.at[idx, "level"] = val
    df = df.sort_values("level", ascending=True)
    conn = get_dbconn("postgis")
    cursor = conn.cursor()
    for cat, gdf in df.groupby("category"):
        # should be a no-op
        if len(gdf.index) == 1:
            continue
        geom_layers = gdf["geom_layers"].values
        levels = gdf["level"].values
        thresholds = gdf["threshold"].values
        for i in range(len(geom_layers) - 1):
            bigger = geom_layers[i]
            smaller = geom_layers[i + 1]
            if levels[i] > 999 or levels[i + 1] > 999:
                continue
            poly = bigger.difference(smaller)
            if not isinstance(poly, MultiPolygon):
                poly = MultiPolygon([poly])
            cursor.execute(
                """
                update spc_outlook_geometries SET geom = %s WHERE
                spc_outlook_id = %s and threshold = %s and category = %s
                """,
                (
                    f"SRID=4326;{poly.wkt}",
                    gdf["id"].values[0],
                    thresholds[i],
                    cat,
                ),
            )
            if cursor.rowcount != 1:
                print("BUG")
                print(gdf)
                sys.exit()
    cursor.close()
    conn.commit()


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        select distinct product_id from spc_outlook where
        extract(year from product_issue) = %s and
        outlook_type in ('C', 'F') ORDER by product_id asc
        """,
        (year,),
    )
    for row in cursor:
        do(row[0])


if __name__ == "__main__":
    main(sys.argv)
