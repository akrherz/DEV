"""Rip the name out to use as a better source.

    ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.txt
"""
import re

from pyiem.util import get_dbconn

LOWERCASE = re.compile("[a-z]")


def main():
    """Go"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    for linenum, line in enumerate(open("isd-history.txt")):
        if linenum < 24:
            continue
        if line[91:93] != "20":
            continue
        name = line[13:43].strip().replace("'", "")
        icao = line[51:55].strip()
        if len(icao) != 4:
            continue
        if icao.startswith("K") or icao.startswith("P"):
            continue
        cursor.execute(
            "SELECT iemid, name from stations where "
            "id = %s and (network ~* 'ASOS' or network ~* 'AWOS')",
            (icao,),
        )
        if cursor.rowcount != 1:
            continue
        row = cursor.fetchone()
        if LOWERCASE.findall(row[1]):
            continue
        if row[1].lower() == name.lower():
            continue
        print("%s %s -> %s" % (icao, row[1], name))
        cursor.execute(
            "UPDATE stations SET name = %s where iemid = %s", (name, row[0])
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
