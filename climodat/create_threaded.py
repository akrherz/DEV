"""Oh boy, create a threaded site."""
# stdlib
import json
import sys

# third party
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()


def main(argv):
    """Go Main Go."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    with open(argv[1], encoding="utf-8") as fh:
        job = json.load(fh)
    network = f"{job['threaded'][:2]}CLIMATE"
    nt = NetworkTable(network, only_online=False)
    # Figure the start and end dates for each station in sids
    for i, sid in enumerate(job["sids"]):
        table = f"alldata_{sid[:2]}"
        cursor2 = get_dbconn("coop").cursor()
        cursor2.execute(
            f"SELECT min(day), max(day) from {table} WHERE station = %s",
            (sid,),
        )
        row = cursor2.fetchone()
        LOG.info(
            "#%s. %s %s %s-%s Tracks:%s",
            i,
            sid,
            nt.sts[sid]["name"],
            row[0],
            row[1],
            nt.sts[sid]["attributes"].get("TRACKS_STATION"),
        )
    # Ask me to clarify what to do.
    queue = []
    for i, sid in enumerate(job["sids"]):
        sdate = input(f"For #{i}, Start Date (YYYY-mm-dd): ")
        edate = input(f"For #{i}, End Date (empty is None, YYYY-mm-dd): ")
        if edate == "":
            edate = None
        queue.append([sid, nt.sts[sid]["iemid"], sdate, edate])

    # Create the station with location being half-way point
    lon = (nt.sts[job["sids"][0]]["lon"] + nt.sts[job["sids"][1]]["lon"]) / 2.0
    lat = (nt.sts[job["sids"][0]]["lat"] + nt.sts[job["sids"][1]]["lat"]) / 2.0
    cursor.execute(
        "INSERT into stations(id, name, network, country, state, "
        "plot_name, online, metasite, geom) VALUES "
        "(%s, %s, %s, 'US', %s, %s, 't', 't', 'SRID=4326;POINT(%s %s)') "
        "RETURNING iemid",
        (
            job["threaded"],
            job["name"],
            network,
            job["threaded"][:2],
            job["name"],
            lon,
            lat,
        ),
    )
    iemid = cursor.fetchone()
    LOG.info("Created station %s with iemid %s", job["threaded"], iemid)
    # Create station_threading entries
    for entry in queue:
        cursor.execute(
            "INSERT into station_threading(iemid, source_iemid, begin_date, "
            "end_date) VALUES (%s, %s, %s, %s)",
            (iemid, entry[1], entry[2], entry[3]),
        )
    # Profit
    cursor.close()
    pgconn.commit()

    # Now copy the data around
    pgconn = get_dbconn("coop")
    for entry in queue:
        table = f"alldata_{entry[0][:2]}"
        cursor = pgconn.cursor()
        cursor.execute(
            f"INSERT into {table}(station, day, high, low, precip, snow, "
            "sday, year, month, snowd, precip_estimated, narr_srad, "
            "merra_srad, hrrr_srad, temp_estimated, "
            "temp_hour, precip_hour) SELECT %s, day, high, low, precip, "
            "snow, sday, year, month, snowd, precip_estimated, narr_srad, "
            "merra_srad, hrrr_srad, temp_estimated, "
            f"temp_hour, precip_hour from {table} WHERE station = %s and "
            "day >= %s and day < %s",
            (
                job["threaded"],
                entry[0],
                entry[2],
                "TOMORROW" if entry[3] is None else entry[3],
            ),
        )
        LOG.info("Inserted %s rows from %s", cursor.rowcount, entry[0])
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
