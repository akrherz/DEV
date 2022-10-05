"""

"""
# stdlb
import subprocess
import glob
import tarfile
import sys
import os
import re

# third party
from pyiem.util import noaaport_text

HAS = "https://www.ncei.noaa.gov/pub/has"
YYYYMMDD = re.compile("([\d]{8})")


def main(argv):
    """Go Main Go."""
    for tarz in glob.glob("*.tar.Z"):
        subprocess.call(f"gunzip -c {tarz} > tmp", shell=True)
        with tarfile.open("tmp") as tarfp:
            for member in tarfp.getmembers():
                if (
                    member.name.find("UB") > -1
                    or member.name.find("UACN") > -1
                ):
                    dt = YYYYMMDD.findall(member.name)[0]
                    data = (
                        tarfp.extractfile(member)
                        .read()
                        .decode("ascii", "ignore")
                    )
                    with open(f"{dt}.txt", "a", encoding="ascii") as fh:
                        fh.write(data)
        subprocess.call(f"mv {tarz} processed/", shell=True)


if __name__ == "__main__":
    main(sys.argv)
