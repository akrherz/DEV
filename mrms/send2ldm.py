"""A part of MRMS recovery when our LDM server hiccups.

- Use lftp mirror -I '*20221001-0[89]*' to web fetch what we want
- find . -name *.gz > listing
- run this script
"""
import os
import subprocess


def main():
    """Go Main Go."""
    sectors = "ALASKA CARIB GUAM HAWAII".split()

    with open("listing", encoding="ascii") as lfh:
        for line in lfh:
            line = line.strip()
            mysect = "CONUS"
            for sector in sectors:
                if line.find(sector) > -1:
                    mysect = sector
            fn = line.split("/")[-1]
            pqstr = f"/nfsdata/realtime/outgoing/grib2/{mysect}/{fn}"
            print(f"{line} -> {pqstr}")
            subprocess.call(
                f"pqinsert -i -f EXP -p '{pqstr}' {line}", shell=True
            )
            os.unlink(line)


if __name__ == "__main__":
    main()
