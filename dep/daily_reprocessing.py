"""We need to reprocess things as that is what we are always doing."""
import datetime
import os
import random
import subprocess

import pandas as pd
from pyiem.dep import EAST, NORTH, SOUTH, WEST, get_cli_fname, read_cli
from pyiem.util import get_dbconn, logger

LOG = logger()
SAVEFILE = "/opt/dep/scripts/cligen/mydays.txt"


def env2database():
    """Do what we found yesterday."""
    if not os.path.isfile(SAVEFILE):
        LOG.warning("savefile %s does not exist", SAVEFILE)
        return
    os.chdir("/opt/dep/scripts/RT")
    cmd = "python env2database.py -s 0 "
    with open(SAVEFILE, "r", encoding="utf-8") as fh:
        for line in fh:
            cmd += f" --date {line.strip()} "
    LOG.info(cmd)
    subprocess.call(cmd, shell=True)


def pick_dates_by_database():
    """Look in the database for dates of interest."""
    pgconn = get_dbconn("idep")
    cursor = pgconn.cursor()
    days = []
    cursor.execute(
        """
        with data as (
            select valid, abs(avg_precip - qc_precip) as diff
            from results_by_huc12
            where scenario = 0 ORDER by diff DESC LIMIT 1000)
        select valid, count(*), max(diff) from data
        GROUP by valid ORDER by count desc
    """
    )
    return days


def edit_clifiles():
    """Now we edit files."""
    # Pick a random CLI point outside the midwest, so to target dates.
    attempt = 0
    clifn = None
    while attempt < 1000:
        attempt += 1
        lon = WEST + 0.1 * random.randint(0, (EAST - WEST) * 10)
        lat = SOUTH + 0.1 * random.randint(0, (NORTH - SOUTH) * 10)
        # Focus on Texas and points east for now
        if lon < -107 or lat > 37:
            continue
        clifn = get_cli_fname(lon, lat)
        if os.path.isfile(clifn):
            break
    LOG.warning("Picking clifile: %s", clifn)
    df = read_cli(clifn)
    today = datetime.date.today()
    # Find highest precip entries with only two breakpoints
    # df = df[df["bpcount"] == 2].sort_values("pcpn", ascending=False)
    df = df.sort_values("rad", ascending=True)
    days = []
    for dt, row in df.iterrows():
        if dt >= pd.Timestamp(today):
            continue
        # Review the date this was processed, so to not redo things recently
        fn = f"/mnt/idep2/data/dailyprecip/{dt:%Y/%Y%m%d}.npy.gz"
        # If this file was modified after 5 July 2022, we skip it
        if os.path.isfile(fn):
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(fn))
            # Our floor for when previous reruns should still be valid
            if mt > datetime.datetime(2023, 7, 1):
                LOG.warning("Skipping %s as it was modified %s", dt, mt)
                continue
        LOG.warning(
            "do %s rad: %s precip: %.2f bpcount: %.0f",
            dt,
            row["rad"],
            row["pcpn"],
            row["bpcount"],
        )
        days.append(dt)
        if len(days) >= 13:
            break
    # write a log file for what work we did
    with open(SAVEFILE, "w", encoding="utf-8") as fh:
        for day in days:
            fh.write(f"{day:%Y-%m-%d}\n")

    # Now we do some work!
    os.chdir("/opt/dep/scripts/cligen")
    for day in days:
        cmd = f"python proctor_tile_edit.py 0 {day:%Y %m %d}"
        LOG.info(cmd)
        subprocess.call(cmd, shell=True)


def main():
    """Go Main Go."""
    # We are fired up from cron, go look for the previous day's work
    env2database()
    # reprocess 10 previous dates
    edit_clifiles()


if __name__ == "__main__":
    main()
