"""Dump products to file."""

import os
import sys

from tqdm import tqdm

from pyiem.util import get_dbconn, noaaport_text


def main(argv):
    """Go Main Go."""
    pgconn = get_dbconn("afos")

    desc = tqdm(range(2001, 2020))
    for year in desc:
        desc.set_description(str(year))
        for seg in ["0106", "0712"]:
            table = f"products_{year}_{seg}"
            cursor = pgconn.cursor("streamer")
            cursor.execute(
                "SELECT data, entered at time zone 'UTC', source, pil "
                f"from {table} WHERE substr(pil, 1, 3) in ('FFS', 'FFW')"
            )
            for row in cursor:
                mydir = "FFW_FFS/%s/%02i/%02i" % (
                    row[1].year,
                    row[1].month,
                    row[1].day,
                )
                if not os.path.isdir(mydir):
                    os.makedirs(mydir)
                with open(
                    "%s/%s_%s_%s.txt"
                    % (mydir, row[1].strftime("%Y%m%d%H%M"), row[2], row[3]),
                    "a",
                ) as fh:
                    fh.write(noaaport_text(row[0]))
            cursor.close()


if __name__ == "__main__":
    main(sys.argv)
