"""
Dump shapefiles for TML warnings.
"""

from pyiem.util import get_dbconn
from geopandas import read_postgis


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")

    # Get events for consideration
    gdf = read_postgis(
        """
        SELECT wfo, phenomena as phenom, significance as sig, eventid as etn,
        status,
        to_char(issue at time zone 'UTC', 'YYYYmmddHH24MI') as issued,
        to_char(expire at time zone 'UTC', 'YYYYmmddHH24MI') as expired,
        to_char(updated at time zone 'UTC', 'YYYYmmddHH24MI') as updated,
        to_char(polygon_begin at time zone 'UTC', 'YYYYmmddHH24MI')
            as polygbeg,
        to_char(polygon_end at time zone 'UTC', 'YYYYmmddHH24MI') as polyend,
        to_char(tml_valid at time zone 'UTC', 'YYYYmmddHH24MI') as tml_time,
        tml_direction as tml_drct,
        tml_sknt,
        tml_geom_line from sbw where tml_geom_line is not null and
        not ST_IsEmpty(tml_geom_line) and status != 'CAN'
    """,
        pgconn,
        index_col=None,
        geom_col="tml_geom_line",
    )
    gdf.to_file("tml_lines.shp")


if __name__ == "__main__":
    main()
