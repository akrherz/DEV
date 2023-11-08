"""Some stations have too much data."""
# stdlib
from datetime import datetime, timedelta

# Third Party
import requests

from pandas.io.sql import read_sql
from pyiem.reference import ncei_state_codes
from pyiem.util import convert_value, get_dbconn, logger

LOG = logger()


def truncate(row, end):
    """Remove data we likely should not have kept."""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    # Go until the end of the month
    for i in range(32):
        dt = end + timedelta(days=i)
        if dt.month != end.month:
            break
    dt -= timedelta(days=1)
    cursor.execute(
        f"DELETE from alldata_{row['id'][:2]} WHERE station = %s and "
        "day > %s",
        (row["id"], dt.date()),
    )
    LOG.info("  removed %s rows after %s", cursor.rowcount, dt)
    cursor.close()
    pgconn.commit()


def do(row):
    """Truncate or whatever."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    # Ask ACIS when this station ended.
    sid = row["id"]
    state = sid[:2]
    acis_sid = ncei_state_codes[state] + sid[2:]
    req = requests.post(
        "http://data.rcc-acis.org/StnMeta",
        json={
            "meta": "valid_daterange,sids,name,ll,elev",
            "elems": "maxt,pcpn",
            "sids": acis_sid,
        },
        timeout=60,
    )
    j = req.json()
    if not j["meta"]:
        LOG.info("No data for %s?", acis_sid)
        return
    meta = j["meta"][0]
    dr = meta["valid_daterange"]
    ar = []
    maxt_end = None
    pcpn_end = None
    if dr[0]:
        maxt_end = datetime.strptime(dr[0][1], "%Y-%m-%d")
        ar.append(maxt_end)
    if dr[1]:
        pcpn_end = datetime.strptime(dr[1][1], "%Y-%m-%d")
        ar.append(pcpn_end)
    LOG.info("%s/%s maxt: %s pcpn: %s", sid, acis_sid, maxt_end, pcpn_end)
    end = max(ar)
    # Find the NWSLI
    nwslis = [x.split()[0] for x in meta["sids"] if x.endswith(" 7")]
    if not nwslis:
        LOG.info("  Failed to find NWSLI for %s", meta["sids"])
        return
    if end < datetime(2021, 3, 15):
        truncate(row, end)
        return
    nwsli = nwslis[0]
    cursor.execute(
        "SELECT iemid from stations where id = %s and network = %s",
        (nwsli, f"{state}_COOP"),
    )
    if cursor.rowcount == 0:
        LOG.info(" Adding coop %s", nwsli)
        cursor.execute(
            "INSERT into stations(id, name, network, country, state, "
            "plot_name, online, metasite, geom, elevation) VALUES "
            "(%s, %s, %s, %s, %s, %s, 't', 't', ST_POINT(%s,%s,4326), %s) "
            "RETURNING iemid",
            (
                nwsli,
                meta["name"],
                f"{state}_COOP",
                "US",
                state,
                meta["name"],
                meta["ll"][0],
                meta["ll"][1],
                convert_value(meta.get("elev", -999), "feet", "meter"),
            ),
        )
    LOG.info("  setting online and no archive_end")
    cursor.execute(
        "UPDATE stations SET archive_end = null, online = 't' "
        "WHERE iemid = %s",
        (row["iemid"],),
    )
    cursor.execute(
        "SELECT iemid from station_attributes where iemid = %s and "
        "attr = 'TRACKS_STATION' ",
        (row["iemid"],),
    )
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT into station_attributes VALUES (%s, %s, %s)",
            (row["iemid"], "TRACKS_STATION", f"{nwsli}|{state}_COOP"),
        )
    cursor.close()
    pgconn.commit()


def main():
    """Go Main Go."""
    df = read_sql(
        "SELECT id, iemid from stations where network ~* 'CLIMATE' and "
        "archive_end = '2021-04-18' ORDER by id ASC",
        get_dbconn("mesosite"),
        index_col=None,
    )
    for _, row in df.iterrows():
        try:
            do(row)
        except Exception as exp:
            LOG.error(exp)


if __name__ == "__main__":
    main()
