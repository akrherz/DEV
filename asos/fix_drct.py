"""Somehow we ended up with directions impossible in METAR."""
import re

from pyiem.util import get_dbconn

WIND_RE = re.compile(r" ([0-9]{3})(\d+)G?(\d*)KT ")


def main(argv):
    """Go Main Go."""
    year = argv[1]
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute(
        f"SELECT station, valid, drct, metar from t{year} "
        "WHERE drct is not null and (drct / 5)::int % 2 = 1 and "
        "metar is not null LIMIT 10000"
    )
    hits = 0
    fails = 0
    for row in cursor:
        m = WIND_RE.findall(row[3])
        if not m:
            fails += 1
            continue
        drct = int(m[0][0])
        if drct == row[2]:
            continue
        cursor2.execute(
            f"UPDATE t{year} SET drct = %s WHERE station = %s "
            "and valid = %s",
            (drct, row[0], row[1]),
        )
        hits += 1
    print(f"{year} {hits}/{cursor.rowcount} rows updated, {fails} fails")
    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    for _year in range(1981, 2009):
        main([None, str(_year)])
