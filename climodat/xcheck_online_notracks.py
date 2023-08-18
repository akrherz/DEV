"""
Any online climodat site should either be TRACKS_STATION or a part of
threading.  This script looks for trouble.
"""

import requests

from pyiem.reference import ncei_state_codes
from pyiem.util import get_dbconn, logger

LOG = logger()
SERVICE = "http://data.rcc-acis.org/StnMeta"


def main():
    """Go Main Go."""
    conn = get_dbconn("mesosite")
    cursor = conn.cursor()
    cursor2 = conn.cursor()
    cursor.execute(
        """
    with data as (
        select id, s.iemid, name, a.attr, a.value from stations s
        LEFT JOIN station_attributes a ON (s.iemid = a.iemid)
        where s.network ~* 'CLIMATE' and s.online and
        substr(id, 3, 1) not in ('C', 'D', 'T')
        and substr(id, 3, 4) != '0000')
    select * from data where value is null
        """
    )
    for row in cursor:
        station = row[0]
        state = station[:2]
        # Query ACIS
        acisid = f"{ncei_state_codes[state]}{station[2:]}"
        payload = {"sids": acisid, "meta": "sid_dates"}
        req = requests.post(SERVICE, json=payload, timeout=60)
        j = req.json()
        meta = j["meta"]
        if not meta:
            LOG.info("ACIS lookup of %s failed, sid: %s", acisid, station)
            continue
        meta = meta[0]
        LOG.info("%s %s", station, meta["sid_dates"])
        track_network = None
        track_station = None
        for entry, sid_start, sid_end in meta["sid_dates"]:
            tokens = entry.split()
            if tokens[1] in ["3", "7"] and track_network is None:
                if tokens[1] == "3" and len(tokens[0]) == 3:
                    track_station = tokens[0]
                    track_network = f"{state}_ASOS"
                if tokens[1] == "7":
                    track_station = tokens[0]
                    track_network = f"{state}_COOP"
        if track_network is None:
            LOG.info("FAIL")
            continue
        # Do we know about this station
        cursor2.execute(
            "SELECT iemid from stations where id = %s and network = %s",
            (track_station, track_network),
        )
        if cursor2.rowcount == 0:
            if track_network.find("COOP") > -1:
                # Likely a DCP we can replicate
                LOG.info("Copying DCP to COOP %s", track_station)
                cursor2.execute(
                    """
                insert into stations
                    (id, network, name, state, country, geom, elevation)
                select id, %s, name, state, country, geom, elevation from
                stations where id = %s and network = %s
                """,
                    (
                        track_network,
                        track_station,
                        track_network.replace("COOP", "DCP"),
                    ),
                )
            else:
                LOG.info(
                    "FAIL, %s[%s] is unknown", track_station, track_network
                )
                continue
        # Is this station being tracked by somebody else?
        tracks = f"{track_station}|{track_network}"
        cursor2.execute(
            "select iemid from station_attributes where value = %s",
            (tracks,),
        )
        if cursor2.rowcount > 0:
            LOG.info("FAIL %s already in use", tracks)
            continue
        LOG.info("%s -> %s", row[1], tracks)
        cursor2.execute(
            """insert into station_attributes values (%s, %s, %s)""",
            (row[1], "TRACKS_STATION", tracks),
        )
    cursor2.close()
    conn.commit()


if __name__ == "__main__":
    main()
