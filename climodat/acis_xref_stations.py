"""Mine the ACIS station cross-reference."""
import sys

import requests

from pyiem.network import Table as NetworkTable
from pyiem.reference import ncei_state_codes
from pyiem.util import get_dbconn, logger

LOG = logger()
SERVICE = "http://data.rcc-acis.org/StnMeta"
MYATTR = "TRACKS_STATION"


def check_coop(nwsli):
    """See if we have current COOPish SHEF data."""
    with get_dbconn("iem") as pgconn:
        cursor = pgconn.cursor()
        cursor.execute(
            "SELECT * from current_shef where station = %s and "
            "physical_code = %s and extremum = %s and value > -50 and "
            "valid > (now() - '120 days'::interval)",
            (nwsli, "TA", "X"),
        )
        rowcount = cursor.rowcount
    return rowcount > 0


def main(argv):
    """Do the query and work."""
    state = argv[1]
    network = f"{state}CLIMATE"
    nt = {
        network: NetworkTable(network, only_online=False),
        f"{state}_COOP": NetworkTable(f"{state}_COOP"),
        f"{state}_ASOS": NetworkTable(f"{state}_ASOS"),
    }
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    for sid in nt[network].sts:
        if sid[2:] == "0000" or sid[2] in ["C", "T", "K"]:
            continue
        current = nt[network].sts[sid]["attributes"].get(MYATTR)
        if current is not None:
            continue
        acis_station = f"{ncei_state_codes[state]}{sid[2:]}"
        payload = {"sids": acis_station, "meta": "sid_dates"}
        req = requests.post(SERVICE, json=payload, timeout=60)
        j = req.json()
        meta = j["meta"]
        if not meta:
            LOG.info("ACIS lookup of %s failed, sid: %s", acis_station, sid)
            continue
        meta = meta[0]
        LOG.info("%s %s", sid, meta["sid_dates"])
        for entry, sid_start, sid_end in meta["sid_dates"]:
            tokens = entry.split()
            if tokens[1] in ["3", "7"]:
                to_track = tokens[0]
                to_network = (
                    f"{state}_{'COOP' if tokens[1] == '7' else 'ASOS'}"
                )
                is_online = sid_end.startswith("9999")
                # Double check
                if is_online and tokens[1] == "7":
                    is_online = check_coop(to_track)
                LOG.info(
                    "    %s [%s-%s][online:%s]-> %s %s",
                    sid,
                    sid_start,
                    sid_end,
                    is_online,
                    to_track,
                    to_network,
                )
                if to_track not in nt[to_network].sts:
                    LOG.info("    ERROR %s is unknown!", to_track)
                    continue
                value = f"{to_track}|{to_network}"
                if tokens[1] == "3":
                    cursor.execute(
                        """
                        UPDATE stations SET temp24_hour = 0, precip24_hour = 0
                        WHERE iemid = %s
                    """,
                        (nt[network].sts[sid]["iemid"],),
                    )
                cursor.execute(
                    "INSERT into station_attributes(iemid, attr, value) "
                    "VALUES (%s, %s, %s)",
                    (nt[network].sts[sid]["iemid"], MYATTR, value),
                )
                if not nt[network].sts[sid]["online"] and is_online:
                    LOG.info("    Setting station online")
                    cursor.execute(
                        "UPDATE stations SET online = 't', archive_end = null "
                        "where iemid = %s",
                        (nt[network].sts[sid]["iemid"],),
                    )
                break
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
