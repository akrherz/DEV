"""Updates the database table denoting if station `HASTAF`"""

from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main Go."""
    asos = get_dbconn("asos")
    acursor = asos.cursor()
    acursor.execute(
        "SELECT distinct station from taf where "
        "valid > now() - '30 days'::interval"
    )
    mesosite = get_dbconn("mesosite")
    cursor = mesosite.cursor()
    for row in acursor:
        station = row[0][1:] if row[0].startswith("K") else row[0]
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
            "attr = 'HASTAF'",
            (iemid,),
        )
        if cursor.rowcount == 1:
            continue
        LOG.info("Setting HASTAF for %s[%s]", station, iemid)
        cursor.execute(
            "INSERT INTO station_attributes (iemid, attr, value) "
            "VALUES (%s, 'HASTAF', %s)",
            (iemid, "1"),
        )
    cursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
