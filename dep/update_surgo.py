"""Update the flowpath_points table with new info."""

from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn('idep')
    cursor = pgconn.cursor()
    updated = 0
    for linenum, line in enumerate(open('/tmp/points_v2_SOL.csv')):
        if linenum == 0:
            continue
        tokens = line.split(",")
        oid = tokens[1]
        oldsurgo = tokens[6]
        newsurgo = tokens[7]
        if oldsurgo == newsurgo:
            continue
        cursor.execute("""
            UPDATE flowpath_points SET surgo = %s where oid = %s
        """, (newsurgo, oid))
        updated += 1
    print("updated %s/%s rows" % (updated, linenum))
    pgconn.commit()


if __name__ == '__main__':
    main()
