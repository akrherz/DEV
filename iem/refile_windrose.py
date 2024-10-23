"""Reorganize wind rose files."""

import calendar
import os
import shutil

from pyiem.util import get_dbconn
from tqdm import tqdm

OLDDIR = "/mesonet/share/windrose/climate"


def main():
    """Go Main Go."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT id, network from stations where network ~* 'ASOS' or "
        "network = 'AWOS' or network ~* 'DCP' ORDER by id ASC"
    )
    for row in tqdm(cursor, total=cursor.rowcount):
        testfn = "%s/yearly/%s_yearly.png" % (OLDDIR, row[0])
        if not os.path.isfile(testfn):
            continue
        cachedir = "/mesonet/share/windrose/%s/%s" % (row[1], row[0])
        if not os.path.isdir(cachedir):
            os.makedirs(cachedir)
        shutil.move(testfn, "%s/%s_yearly.png" % (cachedir, row[0]))
        for i, abbr in enumerate(calendar.month_abbr[1:]):
            abbr = abbr.lower()
            testfn = "%s/monthly/%02i/%s_%s.png" % (
                OLDDIR,
                i + 1,
                row[0],
                abbr,
            )
            if not os.path.isfile(testfn):
                continue
            shutil.move(testfn, "%s/%s_%s.png" % (cachedir, row[0], abbr))


if __name__ == "__main__":
    main()
