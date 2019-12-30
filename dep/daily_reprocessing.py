"""We need to reprocess things as that is what we are always doing."""
import os
import subprocess

from pyiem.util import logger, get_dbconn

LOG = logger()
SAVEFILE = "/opt/dep/scripts/cligen/mydays.txt"


def env2database():
    """Do what we found yesterday."""
    if not os.path.isfile(SAVEFILE):
        LOG.info("savefile %s does not exist", SAVEFILE)
        return
    os.chdir("/opt/dep/scripts/RT")
    cmd = "python env2database.py -s 0 "
    for line in open(SAVEFILE):
        cmd += " --date %s " % (line.strip(),)
    LOG.debug(cmd)
    subprocess.call(cmd, shell=True)


def edit_clifiles():
    """Now we edit files."""
    pgconn = get_dbconn("idep")
    cursor = pgconn.cursor()
    days = []
    cursor.execute(
        """
        select huc_12, valid, qc_precip, avg_precip, max_precip,
        max_precip - qc_precip as diff from results_by_huc12
        where scenario = 0 and qc_precip > max_precip
        ORDER by diff ASC LIMIT 10
    """
    )
    for row in cursor:
        if row[1] not in days:
            LOG.info(
                "do %s qc_precip: %.2f max_precip: %.2f",
                row[1],
                row[2],
                row[4],
            )
            days.append(row[1])
    # write a log file for what work we did
    with open(SAVEFILE, "w") as fh:
        for day in days:
            fh.write("%s\n" % (day.strftime("%Y-%m-%d"),))

    # Now we do some work!
    os.chdir("/opt/dep/scripts/cligen")
    for day in days:
        cmd = "python proctor_tile_edit.py 0 %s" % (day.strftime("%Y %m %d"),)
        LOG.debug(cmd)
        subprocess.call(cmd, shell=True)


def main():
    """Go Main Go."""
    # We are fired up from cron, go look for the previous day's work
    env2database()
    # reprocess 10 previous dates
    edit_clifiles()


if __name__ == "__main__":
    main()
