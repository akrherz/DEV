"""Edit News item."""

import argparse
import sys

from pyiem.util import get_dbconn


def dump(num):
    """Get and dump the news item."""
    dbconn = get_dbconn("mesosite")
    cursor = dbconn.cursor()
    cursor.execute("SELECT body from news WHERE id = %s", (num,))
    row = cursor.fetchone()
    with open(f"{num}.txt", "a") as fp:
        fp.write(row[0])


def update(num):
    """Get and dump the news item."""
    dbconn = get_dbconn("mesosite")
    cursor = dbconn.cursor()
    body = open(f"{num}.txt", "r").read()
    cursor.execute("UPDATE news SET body = %s WHERE id = %s", (body, num))
    cursor.close()
    dbconn.commit()


def usage():
    """Create the argparse instance."""
    parser = argparse.ArgumentParser("Edit IEM News Item")
    parser.add_argument("-g", "--get", required=False, type=int)
    parser.add_argument("-s", "--set", required=False, type=int)
    return parser


def main(argv):
    """Go Main Go."""
    parser = usage()
    args = parser.parse_args(argv[1:])
    if args.get is not None:
        dump(args.get)
    elif args.set is not None:
        update(args.set)


if __name__ == "__main__":
    main(sys.argv)
