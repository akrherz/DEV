"""We need to reprocess things as that is what we are always doing."""
import datetime
import os
import subprocess

from pyiem.util import logger, get_dbconn

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


def edit_clifiles():
    """Now we edit files."""
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
    for row in cursor:
        # Review the date this was processed, so to not redo things recently
        fn = f"/mnt/idep2/data/dailyprecip/{row[0]:%Y/%Y%m%d}.npy.gz"
        # If this file was modified after 25 June 2022, we skip it
        if os.path.isfile(fn):
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(fn))
            if mt > datetime.datetime(2022, 6, 25):
                LOG.warning("Skipping %s as it was modified %s", row[0], mt)
                continue
        LOG.warning(
            "do %s max_delta: %.2f count: %.0f",
            row[0],
            row[2],
            row[1],
        )
        days.append(row[0])
        if len(days) >= 10:
            break
    pgconn.close()
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
