"""Glean what mesonet.org has!

Since ~2006. Directory changes format on 1 Jan 2009"""
import glob
import os
import subprocess
import sys

import pandas as pd
from pyiem.util import noaaport_text, utc


def process(valid):
    """Process for the given valid hour."""
    # Download text
    cmd = valid.strftime(
        "lftp -e 'mget *; quit' http://www.mesonet.org/data/public/noaa/text/"
        "archive/%Y/%m/%d/%H/SA/"
    )
    subprocess.call(cmd, shell=True)
    # Combine into SAO
    with open(f"{valid:%y%m%d%H}.sao", "wb") as fh:
        for fn in sorted(glob.glob("*.txt")):
            with open(fn, encoding="utf-8") as ffh:
                fh.write(noaaport_text(ffh.read()).encode("utf-8"))
            os.unlink(fn)
    # Pipe to metar ingest
    cmd = valid.strftime(
        "cat %y%m%d%H.sao | python /home/meteor_ldm/pyWWA/parsers/"
        "metar_parser.py -x -u %Y-%m-%dT23:59 -l -s 300"
    )
    subprocess.call(cmd, shell=True)

    # Archive it
    storefn = valid.strftime("/mesonet/ARCHIVE/raw/sao/%Y_%m/%y%m%d%H.sao.gz")
    if os.path.isfile(storefn):
        os.rename(storefn, storefn.replace(".sao.gz", "_iem.sao.gz"))
    subprocess.call(f"gzip {valid:%y%m%d%H}.sao", shell=True)
    subprocess.call(f"mv {valid:%y%m%d%H}.sao.gz {storefn}", shell=True)


def auto():
    """Figure out what to do."""
    for dt in pd.date_range("2010/01/01", "2019/01/01", freq="1H"):
        fn = dt.strftime("/mesonet/ARCHIVE/raw/sao/%Y_%m/%y%m%d%H.sao.gz")
        if not os.path.isfile(fn) or os.path.getsize(fn) < 100000:
            print(f"Doing {dt}")
            process(dt)


def main(argv):
    """Go Main."""
    valid = utc(*[int(a) for a in argv[1:]])
    process(valid)


if __name__ == "__main__":
    # main(sys.argv)
    auto()
