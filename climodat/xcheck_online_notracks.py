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
    cursor.execute(
        """
    with data as (
        select id, name, a.attr, a.value from stations s
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
        for entry, sid_start, sid_end in meta["sid_dates"]:
            tokens = entry.split()
            if tokens[1] in ["3", "7"]:
                print(tokens)


if __name__ == "__main__":
    main()
