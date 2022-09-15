"""
Process the giant files from here:
https://www.ncei.noaa.gov/has/HAS.FileAppRouter?datasetname=6431&subqueryby=STATION&applname=&outdest=FILE

"""
# stdlb
import subprocess
import glob
import tarfile
import sys
import os

# third party
from pyiem.util import noaaport_text

HAS = "https://www.ncei.noaa.gov/pub/has"


def main(argv):
    """Go Main Go."""
    order = argv[1]
    bigfn = argv[2]
    subprocess.call(f"wget {HAS}/{order}/{bigfn}", shell=True)
    subprocess.call(f"tar -xzf {bigfn}", shell=True)
    base = bigfn[8:14]
    for tarfn in glob.glob("*.tar"):
        with tarfile.open(tarfn) as tarfp:
            for member in tarfp.getmembers():
                if member.name.startswith("TEXT_SA"):
                    wmo = member.name[5:11]
                    data = (
                        tarfp.extractfile(member)
                        .read()
                        .decode("ascii", "ignore")
                    )
                    tokens = data.split(wmo)
                    for token in tokens:
                        if len(token) < 20:
                            continue
                        # ' XXXX 00__'
                        hr = token[8:10]
                        saofn = f"{base}{hr}.sao"
                        with open(saofn, "a", encoding="ascii") as fh:
                            fh.write(noaaport_text(f"000 \r\r\n{wmo}{token}"))
        os.unlink(tarfn)
    subprocess.call(
        f"rsync -a --remove-source-files {bigfn} mesonet@metl60:/stage/NWSTG/",
        shell=True,
    )


if __name__ == "__main__":
    main(sys.argv)
