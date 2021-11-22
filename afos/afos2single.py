"""Dump products to file."""
import os

from pyiem.util import get_dbconn, noaaport_text


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor("streamer")

    cursor.execute(
        """
        SELECT data, entered at time zone 'UTC', pil, source from products
        WHERE substr(pil, 1, 3) in ('TOR', 'SVR', 'SVS') and
        entered >= '2007-01-01 00:00+00'
    """
    )
    for row in cursor:
        pil = row[2].strip()
        mydir = f"{row[3]}/{pil}"
        if not os.path.isdir(mydir):
            os.makedirs(mydir)
        fn = row[1].strftime(f"{mydir}/{pil}_%Y%m%d%H%M.txt")
        with open(fn, "a", encoding="utf8") as fh:
            fh.write(noaaport_text(row[0]))


if __name__ == "__main__":
    main()
