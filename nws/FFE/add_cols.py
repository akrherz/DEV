"""Add columns."""

import pandas as pd
from pyiem.util import get_dbconn

SAVECOLS = [
    "source",
    "eventid",
    "phenomena",
    "significance",
    "year",
    "link",
    "utc_valid",
    "expire",
]


def main():
    """Go MAin"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    df = pd.read_csv("flood_emergencies_2019.csv")
    df2 = df[SAVECOLS].drop_duplicates().copy()
    df2["polygon_area_sqkm"] = None
    for _i, row in df2.iterrows():
        cursor.execute(
            """
        SELECT ST_area(geom::geography) from sbw WHERE wfo = %s and
        phenomena = %s and significance = %s and eventid = %s and
        extract(year from issue) = %s and status = 'NEW'
        """,
            (
                row["source"][1:],
                row["phenomena"],
                row["significance"],
                row["eventid"],
                row["year"],
            ),
        )
        res = cursor.fetchone()
        if res is not None:
            df2.at[_i, "polygon_area_sqkm"] = res[0] / 1e6

    df2.to_csv("flood_emergencies_2019_v2.csv", index=False)


if __name__ == "__main__":
    main()
