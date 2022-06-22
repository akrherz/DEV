"""List outages based on my archiving."""
import datetime
import glob
import os
import sys


def get_scans_for_date(radar, ts):
    """
    Figure out our volume scans for a given date
    """
    dirname = ts.strftime(
        f"/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/{radar}/N0Q"
    )
    if not os.path.isdir(dirname):
        return
    os.chdir(dirname)
    files = glob.glob("*.png")
    files.sort()
    for file in files:
        yield datetime.datetime.strptime(file[8:20], "%Y%m%d%H%M")


def main(argv):
    """Go Main Go."""
    radar = argv[1]
    sts = datetime.datetime(2020, 1, 1)
    ets = datetime.datetime(2020, 7, 20)
    interval = datetime.timedelta(days=1)
    valid = sts
    now = sts
    while now < ets:
        for scan in get_scans_for_date(radar, now):
            delta = scan - valid
            if delta > datetime.timedelta(hours=1):
                print(f"{valid} {scan} {delta}")
            valid = scan
        now += interval


if __name__ == "__main__":
    main(sys.argv)
