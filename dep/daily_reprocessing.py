"""We need to reprocess things as that is what we are always doing."""
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
            select huc_12, valid, qc_precip, avg_precip, max_precip,
            abs(max_precip - qc_precip) as diff from results_by_huc12
            where scenario = 0 ORDER by diff DESC LIMIT 1000)
        select valid, count(*), max(diff) from data
        GROUP by valid ORDER by count desc
    """
    )
    for row in cursor:
        if row[1] not in days:
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
