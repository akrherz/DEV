"""Process the METARs found at TGFTP."""

import os
import re
import sys
from datetime import datetime

import requests
from psycopg2.extras import DictCursor
from pyiem.nws.products.metarcollect import METARReport
from pyiem.util import exponential_backoff, get_dbconn, logger

LOG = logger()
URLBASE = "https://tgftp.nws.noaa.gov/data/observations/metar/cycles/"
TIMERE = re.compile(
    "^20[0-9][0-9]/[0-2][0-9]/[0-3][0-9] [0-2][0-9]:[0-5][0-9]$"
)


def build_xref():
    """Need networks / iemids to make this work."""
    dbconn = get_dbconn("mesosite")
    cursor = dbconn.cursor()
    cursor.execute(
        "SELECT id, iemid, network, tzname from stations "
        "where (network = 'AWOS' or network ~* 'ASOS') and tzname is not null"
    )
    xref = {}
    for row in cursor:
        xref[row[0]] = {"iemid": row[1], "network": row[2], "tzname": row[3]}
    return xref


def get_file(fn):
    """Get the file from the server."""
    req = exponential_backoff(requests.get, f"{URLBASE}{fn}", timeout=20)
    tmpfn = f"/tmp/{fn}"
    with open(tmpfn, "wb") as fh:
        fh.write(req.content)
    return tmpfn


def main(argv):
    """Go Main Go."""
    fn = get_file(argv[1])
    xref = build_xref()
    pgconn = get_dbconn("iem")
    valid = None
    (failures, success) = (0, 0)
    with open(fn, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line == "":
                valid = None
                continue
            if TIMERE.match(line):
                valid = datetime.strptime(line, "%Y/%m/%d %H:%M")
                continue
            # Must have an ob!
            try:
                mtr = METARReport(line, month=valid.month, year=valid.year)
            except Exception:
                failures += 1
                continue
            lookup = line[:4] if not line.startswith("K") else line[1:4]
            if lookup not in xref:
                LOG.info("Unknown %s", lookup)
                continue
            mtr.iemid = lookup
            mtr.network = xref[lookup]["network"]
            mtr.tzname = xref[lookup]["tzname"]
            cursor = pgconn.cursor(cursor_factory=DictCursor)
            mtr.to_iemaccess(cursor, force_current_log=True)
            cursor.close()
            pgconn.commit()
            success += 1
    LOG.info("Processed %s failures %s", success, failures)
    os.unlink(fn)


if __name__ == "__main__":
    main(sys.argv)
