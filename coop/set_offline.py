"""Check for IEM online COOP sites without data."""

import sys

import requests
from pyiem.database import get_dbconnc
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()
SERVICE = "http://data.rcc-acis.org/StnMeta"


def main(argv):
    """Go Main."""
    network = f"{argv[1]}_COOP"
    nt = NetworkTable(network)
    iem, icursor = get_dbconnc("iem")
    mesosite, mcursor = get_dbconnc("mesosite")

    for sid in nt.sts:
        # Does this station have any data over the past year?
        icursor.execute(
            """SELECT count(*) from summary s JOIN stations t on
            (s.iemid = t.iemid) WHERE s.day > now() - '1 year'::interval
            and t.id = %s and t.network = %s and
            (max_tmpf is not null or min_tmpf is not null or
            pday is not null)
            """,
            (sid, network),
        )
        obscnt = icursor.fetchone()["count"]
        if obscnt > 0:
            continue
        LOG.info("%s has %s rows of data", sid, obscnt)
        # Is this station offline in ACIS (sid_dates is defined)
        payload = {"sids": sid, "meta": "sid_dates"}
        req = requests.post(SERVICE, json=payload, timeout=60)
        j = req.json()
        meta = j["meta"]
        if meta:
            meta = meta[0]
            online = False
            for _entry, _sid_start, sid_end in meta["sid_dates"]:
                if sid_end.startswith("9999"):
                    online = True
            if online:
                continue
        else:
            # Check if this is dual listed
            mcursor.execute(
                "SELECT iemid from stations where id = %s and network = %s",
                (sid, f"{argv[1]}_DCP"),
            )
            if mcursor.rowcount == 1:
                LOG.info("%s is dual listed, deleting", sid)
                mcursor.execute(
                    "delete from stations where id = %s and network = %s",
                    (sid, f"{argv[1]}_COOP"),
                )
            else:
                LOG.info("%s is not dual listed, setting to DCP", sid)
                mcursor.execute(
                    "update stations SET network = %s "
                    "where id = %s and network = %s",
                    (f"{argv[1]}_DCP", sid, f"{argv[1]}_COOP"),
                )

        # Does this station have a climodat tracker?
        mcursor.execute(
            """
            SELECT t.iemid, t.id, t.network, t.online
            from station_attributes a JOIN stations t
            ON (a.iemid = t.iemid) where attr = 'TRACKS_STATION'
            and value = %s
            """,
            (f"{sid}|{network}",),
        )
        if mcursor.rowcount > 0:
            meta = mcursor.fetchone()
            LOG.info(
                "%s tracks %s[%s] %s",
                sid,
                meta["id"],
                meta["network"],
                meta["online"],
            )
            if meta["online"]:
                LOG.info(
                    "Setting %s[%s] to offline", meta["id"], meta["network"]
                )
                mcursor.execute(
                    "UPDATE stations SET online = 'f' where iemid = %s",
                    (meta["iemid"],),
                )

        LOG.info("    ----> Setting %s offline", sid)
        # Set offline
        mcursor.execute(
            "UPDATE stations SET online = 'f' where iemid = %s",
            (nt.sts[sid]["iemid"],),
        )
        # Remove current year summary entries
        icursor.execute(
            "delete from summary_2023 WHERE iemid = %s",
            (nt.sts[sid]["iemid"],),
        )
        mcursor.close()
        mesosite.commit()
        icursor.close()
        iem.commit()
        mcursor = mesosite.cursor()
        icursor = iem.cursor()
        LOG.info("\n\n\n")
    iem.close()
    mesosite.close()


if __name__ == "__main__":
    main(sys.argv)
