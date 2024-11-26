"""Find ASOS stations that should be culled."""

from pyiem.database import get_dbconn


def check(station, network):
    """See if this should be removed?"""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT valid from alldata where station = %s LIMIT 5", (station,)
    )
    if cursor.rowcount == 5:
        print(f"station: {station} network: {network} has data?")
        return
    print(f"{network} {station} {cursor.rowcount}")
    with open("jobs.sh", "a", encoding="utf-8") as fh:
        fh.write(f"python delete_station.py {network} {station}\n")


def main():
    """Go Main Go."""
    print("CAUTION!!! Don't delete stations that only exist for ASOS 1 Min")
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT id, network from stations where network ~* 'ASOS' "
        "and archive_begin is null and archive_end is null "
        "ORDER by id ASC"
    )
    for row in cursor:
        check(row[0], row[1])


if __name__ == "__main__":
    main()
