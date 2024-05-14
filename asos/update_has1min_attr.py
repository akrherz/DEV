"""Updates the database table denoting if station `HAS1MIN`"""

import httpx

from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()
INV = (
    "https://www.ncei.noaa.gov/pub/data/asos-onemin/"
    "Inventory/Om2MonthInventory202405.Report2"
)
HAS1MIN = "HAS1MIN"


def main():
    """Go Main Go."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    req = httpx.get(INV)
    if req.status_code != 200:
        LOG.info("Ooops, got %s for %s", req.status_code, INV)
        return
    for linenum, line in enumerate(req.text.split("\n")):
        if linenum < 5 or len(line) < 10:
            continue
        station = line[:4]
        station = station[1:] if station[0] == "K" else station
        cursor.execute(
            "SELECT iemid from stations where id = %s and network ~* 'ASOS'",
            (station,),
        )
        if cursor.rowcount == 0:
            LOG.info("station %s is unknown to metadata", station)
            continue
        iemid = cursor.fetchone()[0]
        cursor.execute(
            "SELECT * from station_attributes where iemid = %s and "
            "attr = %s",
            (iemid, HAS1MIN),
        )
        if cursor.rowcount == 1:
            continue
        LOG.info("Setting %s for %s[%s]", HAS1MIN, station, iemid)
        cursor.execute(
            "INSERT INTO station_attributes (iemid, attr, value) "
            "VALUES (%s, %s, %s)",
            (iemid, HAS1MIN, "1"),
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
