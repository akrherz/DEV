"""Correct some bad gust data that went into the database.

see akrherz/iem#188"""

import re

from pyiem.util import get_dbconn

WIND_RE = re.compile(r" [0-9]{3}(\d+)G(\d+)KT ")


def main(argv):
    """Go Main Go."""
    year = argv[1]
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute(
        f"SELECT station, valid, sknt, gust, metar from t{year} "
        "WHERE round(gust::numeric, 2) != gust::int"
    )
    hits = 0
    for row in cursor:
        m = WIND_RE.findall(row[4])
        if not m:
            continue
        sknt, gust = m[0]
        dirty = False
        if int(sknt) != row[2]:
            # print("sknt old: %s new: %s" % (row[2], int(sknt)))
            dirty = True
        if int(gust) != row[3]:
            # print("gust old: %s new: %s" % (row[3], int(gust)))
            dirty = True
        if not dirty:
            continue
        cursor2.execute(
            f"UPDATE t{year} SET sknt = %s, gust = %s WHERE station = %s "
            "and valid = %s",
            (sknt, gust, row[0], row[1]),
        )
        hits += 1
    print(f"{year} {hits}/{cursor.rowcount} rows updated")
    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    for _year in range(1929, 1990):
        main([None, str(_year)])
