"""fix the climate_file in the database"""

from tqdm import tqdm

from pyiem.dep import get_cli_fname
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("idep")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute(
        """
    SELECT distinct climate_file, scenario from flowpaths
    where climate_file != 'cli/all.cli'
    """
    )
    for row in tqdm(cursor, total=cursor.rowcount):
        (lon, lat) = [float(x) for x in row[0].split("/")[-1][:-4].split("x")]
        lon = 0 - lon
        fn = get_cli_fname(lon, lat, row[1])
        cursor2.execute(
            """
        UPDATE flowpaths SET climate_file = %s where climate_file = %s
        and scenario = %s
        """,
            (fn, row[0], row[1]),
        )
    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
