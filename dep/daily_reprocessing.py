"""We need to reprocess things as that is what we are always doing."""

import datetime
import os
import subprocess
from typing import Optional, Tuple

import click
import pandas as pd
from pyiem.database import get_dbconn
from pyiem.dep import read_cli
from pyiem.util import logger

SIZE = 13
LOG = logger()
SAVEFILE = "/opt/dep/scripts/cligen/mydays.txt"
THRESHOLD_DATE = datetime.datetime(2024, 2, 1)


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


def pick_dates_by_neighbor_diff() -> Tuple[str]:
    """Repair an off-by one that caused some grief."""
    c1 = read_cli("/i/0/cli/094x042/094.56x042.98.cli")
    c2 = read_cli("/i/0/cli/094x042/094.56x042.99.cli")
    candidates = (c2["pcpn"] - c1["pcpn"]).abs().sort_values(ascending=False)
    days = []
    for dt, diff in candidates.items():
        mt = get_update_date(dt)
        LOG.warning(
            "Processing %s[mod:%s] with diff: %s",
            dt,
            mt.date(),
            diff,
        )
        days.append(dt)
        if len(days) > SIZE:
            break
    return days


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
    for row in cursor:
        mt = get_update_date(row[0])
        if mt < THRESHOLD_DATE:
            LOG.warning(
                "Processing %s[mod:%s] with count: %s diff: %s",
                row[0],
                mt.date(),
                row[1],
                row[2],
            )
            days.append(row[0])
        if len(days) > SIZE:
            break
    pgconn.close()
    return days


def pick_dates_by_moddate() -> Tuple[str]:
    """Find files to reprocess by their age."""
    days = []
    for dt in pd.date_range("2007/01/01", datetime.date.today()):
        mt = get_update_date(dt)
        if mt < THRESHOLD_DATE:
            LOG.info("Processing %s[mod:%s]", dt.date(), mt.date())
            days.append(dt)
        if len(days) > SIZE:
            break
    return days


def get_update_date(dt):
    """Filter days that should not be reprocessed."""
    fn = f"/mnt/idep2/data/dailyprecip/{dt:%Y/%Y%m%d}.geotiff"
    mt = datetime.datetime(2050, 1, 1)
    if os.path.isfile(fn):
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(fn))
    return mt


def edit_clifiles(days):
    """Now we edit files."""
    # write a log file for what work we did
    with open(SAVEFILE, "w", encoding="utf-8") as fh:
        for day in days:
            fh.write(f"{day:%Y-%m-%d}\n")

    # Now we do some work!
    os.chdir("/opt/dep/scripts/cligen")
    for day in days:
        cmd = [
            "python",
            "proctor_tile_edit.py",
            "--scenario=0",
            f"--date={day:%Y-%m-%d}",
        ]
        LOG.info(" ".join(cmd))
        subprocess.call(cmd)


@click.command()
@click.option("--clifile", help="Review CLI file for dates to run.")
@click.option("--dryrun", is_flag=True, default=False, help="Dry Run.")
@click.option(
    "--algo",
    type=click.Choice(["database", "moddate", "neighbor"]),
    default="database",
    help="Algorithm to use",
)
def main(clifile: Optional[str], dryrun: bool, algo: str):
    """Go Main Go."""
    if clifile:
        clidf = read_cli(clifile).loc[: datetime.date.today()]
        days = []
        for dt, row in (
            clidf[clidf["bpcount"] == 2]
            .sort_values("pcpn", ascending=False)
            .iterrows()
        ):
            mt = get_update_date(dt)
            if mt < THRESHOLD_DATE:
                LOG.warning(
                    "Processing %s[mod:%s] with pcpn: %s",
                    dt.date(),
                    mt.date(),
                    row["pcpn"],
                )
                days.append(dt)
            if len(days) > SIZE:
                break
    elif algo == "neighbor":
        days = pick_dates_by_neighbor_diff()
    elif algo == "database":
        days = pick_dates_by_database()
    else:
        days = pick_dates_by_moddate()
    if not dryrun:
        env2database()
        LOG.warning("Processing %s days", len(days))
        edit_clifiles(days)


if __name__ == "__main__":
    main()
