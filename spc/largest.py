"""Print out the largest outlooks"""

from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go Please"""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        """WITH data as (
        SELECT category, threshold,
        geom, valid,
        rank() OVER
          (PARTITION by category, threshold ORDER by ST_Area(geom) DESC)
        from spc_outlook o JOIN spc_outlook_geometries g
        on (o.id = g.spc_outlook_id) where day = 1 and outlook_type = 'C'
        ORDER by category, threshold)
    SELECT category, threshold,
    st_area(st_transform(geom, 5070)) / 1000000. * 0.386102 as area,
    valid from data where rank = 1 ORDER by category, threshold
    """,
        pgconn,
        index_col=None,
    )
    for _, row in df.iterrows():
        print(
            ("%-12s %-4s %6.0f %s %s")
            % (
                row["category"],
                row["threshold"],
                row["area"] / 1000.0,
                row["valid"].strftime("%b %d, %Y"),
                row["valid"],
            )
        )


if __name__ == "__main__":
    main()
