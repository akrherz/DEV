"""Fix some database constraints.

NOTE: The present year may still have events active from the previous year,
so that year's constraint may need to be more open ended.
"""
import sys
from datetime import timedelta

from pyiem.database import get_dbconn


def main():
    """."""
    pgconn = get_dbconn("postgis")
    for year in range(2022, 2024):
        cursor = pgconn.cursor()
        cursor.execute(
            f"""
            select min(polygon_begin), max(polygon_begin) from sbw_{year}
            """
        )
        row = cursor.fetchone()
        if (row[1] - row[0]) > timedelta(days=500):
            print(f"{year} {row[0]} {row[1]}")
            sys.exit()
        cursor.execute(
            f"""
            alter table sbw_{year} add constraint
            sbw_{year}_polygon_begin_check CHECK (
                polygon_begin >= '{row[0]}' and polygon_begin <= '{row[1]}')
            """
        )
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
