"""Process GHCNh files into IEM Access, so destined for ASOS database."""

import os
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional

import click
from metar.Metar import Metar
from pyiem.database import get_dbconnc, get_sqlalchemy_conn, sql_helper
from pyiem.ncei.ghcnh import process_file
from pyiem.nws.products.metar_util import metar_from_dict
from pyiem.nws.products.metarcollect import to_iemaccess
from pyiem.observation import Observation
from pyiem.util import logger

LOG = logger()
COUNTERS = defaultdict(lambda: 0)


@dataclass
class PROCESSING_CONTEXT:
    """Processing context."""

    icao: str = ""
    iemid: int = 0
    tzname: str = ""
    ghcnh_id: str = ""
    dbhas: list[str] = field(default_factory=list)
    doublecheck: bool = False
    dbhas_year: int = 1800


def get_metadata(icao: str) -> Optional[tuple[int, str, str]]:
    """Figure out some needed metadata."""
    station = icao if not icao.startswith("K") else icao[1:]
    with get_sqlalchemy_conn("mesosite") as conn:
        res = conn.execute(
            sql_helper("""
                select s.iemid, tzname, value as ghcnh_id from stations s
                JOIN station_attributes a on (s.iemid = a.iemid)
                where id = :station and network ~* 'ASOS' and attr = 'GHCNH_ID'
            """),
            {"station": station},
        )
        if res.rowcount == 0:
            LOG.warning("FATAL: Failed to find metadata for %s", station)
            sys.exit()
        return res.first()


def fetch_file(ghcnh_id: str) -> str:
    """Download the file, if necessary."""
    fn = f"GHCNh_{ghcnh_id}_por.psv"
    if not os.path.isfile(fn):
        subprocess.call(
            [
                "wget",
                (
                    "https://www.ncei.noaa.gov/oa/"
                    "global-historical-climatology-network/hourly/"
                    f"access/by-station/GHCNh_{ghcnh_id}_por.psv"
                ),
            ]
        )
    return fn


def load_dbhas(conn, ctx: PROCESSING_CONTEXT):
    """Figure out what we have in the database."""
    ctx.doublecheck = ctx.dbhas_year > 1996
    table = f"t{ctx.dbhas_year}"
    res = conn.execute(
        sql_helper(
            """
        select to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI'),
    to_char((valid + '13 minutes'::interval) at time zone 'UTC',
            'YYYYMMDDHH24')
        from {table} WHERE station = :station
        and report_type in (3, 4) ORDER by valid ASC
    """,
            table=table,
        ),
        {"station": ctx.icao[1:] if ctx.icao.startswith("K") else ctx.icao},
    )
    dbhas = []
    for rr in res:
        dbhas.append(rr[0])
        if ctx.doublecheck:
            dbhas.append(rr[1])
    LOG.info("Found %s timestamps in %s", len(dbhas), table)
    ctx.dbhas = dbhas


def workflow(conn, icursor, obdict: dict, ctx: PROCESSING_CONTEXT):
    """Do some work."""
    # ASOS + IEMAccess Summary only supports 1900+
    if obdict["valid"].year < 1901:
        COUNTERS["pre1901"] += 1
        return

    if obdict["valid"].year != ctx.dbhas_year:
        ctx.dbhas_year = obdict["valid"].year
        load_dbhas(conn, ctx)

    if obdict["valid"].strftime("%Y%m%d%H%M") in ctx.dbhas:
        COUNTERS["exactdupe"] += 1
        return
    # Situation is that there are METARs with a valid time just
    # outside of the GHCNh data
    if (
        ctx.doublecheck
        and obdict["valid"].minute >= 50
        and (obdict["valid"] + timedelta(minutes=10)).strftime("%Y%m%d%H")
        in ctx.dbhas
    ):
        COUNTERS["likelydupe"] += 1
        return
    if obdict["raw"] is not None and obdict["raw"].find(ctx.icao) > -1:
        # We give it one shot to get right, if it failes, we still
        # save the raw METAR to the database, but used the processed values
        try:
            mtr = Metar(
                obdict["raw"] + " IEM_GHCNH",
                obdict["valid"].month,
                obdict["valid"].year,
            )
            to_iemaccess(
                icursor,
                mtr,
                ctx.iemid,
                ctx.tzname,
                force_current_log=True,
                skip_current=True,
            )
            COUNTERS["usedmetar"] += 1
            return
        except Exception as exp:
            COUNTERS["badmetars"] += 1
            LOG.info("METAR `%s` failed", obdict["raw"])
            LOG.exception(exp)
    else:
        obdict["raw"] = metar_from_dict(obdict) + " IEM_GHCNH"
        if obdict["raw"].endswith("AUTO /////KT RMK AO2 IEM_GHCNH"):
            COUNTERS["nodata"] += 1
            return
    LOG.info(
        "New %s[%s] %s",
        ctx.icao,
        obdict["valid"],
        obdict["raw"],
    )
    iemob = Observation(
        iemid=ctx.iemid, valid=obdict["valid"], tzname=ctx.tzname
    )
    iemob.data.update(obdict)
    iemob.save(icursor, force_current_log=True)
    COUNTERS["new"] += 1


@click.command()
@click.option("--icao", required=True, help="ICAO Identifier")
@click.option("--downloadonly", is_flag=True, help="Just download the file")
@click.option("--savefile", is_flag=True, help="Do not delete the file")
@click.option("--parseonly", is_flag=True, help="Just parse the file")
def main(
    icao: str, downloadonly: bool, savefile: bool, parseonly: bool
) -> None:
    """Go Main."""
    ctx = PROCESSING_CONTEXT()
    ctx.icao = icao
    ctx.iemid, ctx.tzname, ctx.ghcnh_id = get_metadata(icao)
    fn = fetch_file(ctx.ghcnh_id)
    if downloadonly:
        LOG.info("Exiting due to downloadonly flag")
        return
    iconn, icursor = get_dbconnc("iem")
    with get_sqlalchemy_conn("asos") as conn:
        for obdict in process_file(fn):
            # Needed for METAR generation
            obdict["station"] = icao
            COUNTERS["lines"] += 1
            if parseonly:
                continue
            workflow(conn, icursor, obdict, ctx)
            if COUNTERS["new"] > 0 and COUNTERS["new"] % 100 == 0:
                icursor.close()
                iconn.commit()
                icursor = iconn.cursor()

    icursor.close()
    iconn.commit()

    for key, val in COUNTERS.items():
        LOG.info("%s: %s", key, val)
    if not savefile:
        os.unlink(fn)


if __name__ == "__main__":
    main()
