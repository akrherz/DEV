"""fix the climate_file in the database"""

from pyiem.util import get_dbconn
from pyiem.dep import get_cli_fname


def main():
    """Go Main Go"""
    pgconn = get_dbconn("idep")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute("""SELECT distinct climate_file, scenario from flowpaths""")
    for row in cursor:
        (lon, lat) = [float(x) for x in row[0].split("/")[-1][:-4].split("x")]
        lon = 0 - lon
        fn = get_cli_fname(lon, lat, row[1])
        cursor2.execute("""
        UPDATE flowpaths SET climate_file = %s where climate_file = %s
        and scenario = %s
        """, (fn, row[0], row[1]))
    cursor2.close()
    pgconn.commit()


if __name__ == '__main__':
    main()
