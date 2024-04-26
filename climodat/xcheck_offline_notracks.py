"""
Double check offline stations, maybe we can fix.
"""

import requests
from sqlalchemy import text

from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.reference import ncei_state_codes
from pyiem.util import logger

LOG = logger()
SERVICE = "https://data.rcc-acis.org/StnMeta"


def investigate(station):
    """ACIS says online, IEM says otherwise."""
    # Figure out who this station is tracking
    sql = """
    select value from stations t JOIN station_attributes a on
    (t.iemid = a.iemid) WHERE t.id = :station and a.attr = 'TRACKS_STATION'
    """
    with get_sqlalchemy_conn("mesosite") as conn:
        res = conn.execute(text(sql), {"station": station})
        if res.rowcount == 0:
            LOG.info("No TRACKS for %s", station)
            return
        (tracks_station, tracks_network) = res.fetchone()[0].split("|")
    # Go look at IEM access for recent high AND precip data, we need both
    sql = """
    select max(day) from summary_2024 s JOIN stations t on
    (s.iemid = t.iemid) where t.id = :station and t.network = :network
    and max_tmpf is not null and pday is not null
    """
    with get_sqlalchemy_conn("iem") as conn:
        res = conn.execute(
            text(sql),
            {"station": tracks_station, "network": tracks_network},
        )
        maxdate = res.fetchone()[0]
    LOG.info(
        "Station %s tracks %s %s, access maxdate: %s",
        station,
        tracks_network,
        tracks_station,
        maxdate,
    )
    if maxdate is None:
        return
    # Now we need to update the station to be online
    sql = """
    update stations SET online = 't', archive_end = null
    WHERE id = :station and network ~* 'CLIMATE'
    """
    with get_sqlalchemy_conn("mesosite") as conn:
        conn.execute(text(sql), {"station": station})
        conn.commit()


def main():
    """Go Main Go."""
    conn = get_dbconn("mesosite")
    cursor = conn.cursor()
    cursor.execute(
        """
        select id, iemid from stations where network ~* 'CLIMATE'
        and archive_end > '2023-01-01' and not online ORDER by id asc
        """
    )
    for row in cursor:
        station = row[0]
        state = station[:2]
        # Query ACIS
        acisid = f"{ncei_state_codes[state]}{station[2:]}"
        payload = {
            "sids": acisid,
            "meta": "valid_daterange",
            "elems": "maxt,mint,pcpn",
        }
        req = requests.post(SERVICE, json=payload, timeout=60)
        j = req.json()
        meta = j["meta"]
        if not meta:
            LOG.info("ACIS lookup of %s failed, sid: %s", acisid, station)
            continue
        meta = meta[0]
        if any(not x for x in meta["valid_daterange"]):
            LOG.info("ACIS says %s has no data for one var", station)
            continue
        LOG.info("%s %s", station, meta["valid_daterange"])
        for data_start, data_end in meta["valid_daterange"]:
            if data_start.startswith(("9999", "0001")):
                continue
            if data_end > "2024-04-01":
                LOG.info(
                    "ACIS says online? %s %s", station, meta["valid_daterange"]
                )
                investigate(station)
                break


if __name__ == "__main__":
    main()
