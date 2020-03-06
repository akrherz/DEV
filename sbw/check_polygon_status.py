"""Check the final VTEC status for polygons against UGC database.

see akrherz/pyIEM#207
"""
import sys

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main(argv):
    """check things out."""
    year = argv[1]
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    df = read_sql(
        """
        with ugc_based as (
            SELECT distinct wfo, eventid, updated
            from warnings_"""
        + year
        + """
            WHERE phenomena = 'FL' and significance = 'W'
            and status = 'CAN'),
        sbw_based as (
            select distinct wfo, eventid from sbw_"""
        + year
        + """
            WHERE phenomena = 'FL' and significance = 'W'
            and status = 'CAN'
        )
        select u.wfo, u.eventid, u.updated
        from ugc_based u LEFT JOIN sbw_based s
        on (u.wfo = s.wfo and u.eventid = s.eventid) WHERE
        s.wfo is null ORDER by u.updated ASC
    """,
        pgconn,
    )
    print(df)


if __name__ == "__main__":
    main(sys.argv)
