"""Dump products to file."""
import os

from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor("streamer")

    cursor.execute(
        """
        SELECT data, entered at time zone 'UTC', pil from products
        WHERE substr(pil, 1, 3) in ('MWS', 'FLS', 'ZFP', 'CWF') and
        source = 'TJSJ'
        and entered >= '2020-08-01 00:00+00' and entered < '2021-02-01 00:00+00'
    """
    )
    for row in cursor:
        pil = row[2].strip()
        mydir = f"TJSJ/{pil}"
        if not os.path.isdir(mydir):
            os.makedirs(mydir)
        fn = row[1].strftime(f"{mydir}/{pil}_%Y%m%d%H%M.txt")
        with open(fn, "a") as fh:
            fh.write(row[0])


if __name__ == "__main__":
    main()
