"""Rectify threaded station metadata.

I made some bad life choices when I first setup the threaded stations.  This
uber script attempts to straighten out the mess.
"""

import datetime

import requests

import pandas as pd
from pyiem.reference import ncei_state_codes
from pyiem.util import get_dbconn, get_sqlalchemy_conn, logger

code2state = dict((v, k) for k, v in ncei_state_codes.items())
LOG = logger()


def find_candidates():
    """Figure out who needs help."""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            """
            SELECT id as station, t.iemid, a.value as tracks
            from stations t JOIN
            station_attributes a on (t.iemid = a.iemid) WHERE
            network ~* 'CLIMATE' and substr(id, 3, 1) = 'T' and
            a.attr = 'TRACKS_STATION'
            """,
            conn,
            index_col="station",
        )
    LOG.info("Found %s candidates", len(df.index))
    return df


def get_threading_info(threadinfo, station):
    """Figure out what ACIS says."""
    lookfor = station[3:]
    df = None
    for sid, entry in threadinfo.items():
        if sid != lookfor:
            continue
        df = pd.DataFrame(entry)
        break
    if df is None:
        return None
    for idx, row in df.iterrows():
        # Figure out what ACIS thinks of this station id
        payload = {"meta": "sid_dates,ll,name", "sids": row["id"]}
        data = requests.post(
            "https://data.rcc-acis.org/StnMeta",
            json=payload,
            timeout=60,
        ).json()
        # Does this id map back to a COOPish id (#2)
        candidates = []
        for sinfo, sdate, edate in data["meta"][0]["sid_dates"]:
            if not sinfo.endswith(" 2"):
                continue
            candidates.append([sinfo.split()[0], sdate, edate])
        if len(candidates) == 0:
            LOG.info("Found no COOP id for %s", row["id"])
            continue
        if len(candidates) > 1:
            # Pick the one with an end date of 9999
            for entry in candidates:
                if entry[2].startswith("9999"):
                    candidates[0] = entry
        # Now we are ready to update the data frame
        sid = candidates[0][0]
        df.at[idx, "acis_id"] = sid
        df.at[idx, "iem_id"] = f"{code2state[sid[:2]]}{sid[2:]}"
    return df


def check_and_add(mesosite, thrdf):
    """Ensure we have info for these sites."""
    cursor = mesosite.cursor()
    for idx, row in thrdf.iterrows():
        if pd.isna(row["iem_id"]):
            continue
        cursor.execute(
            "SELECT iemid from stations where id = %s", (row["iem_id"],)
        )
        if cursor.rowcount == 0:
            input(f"Please add {row['iem_id']} to database acis: {row['id']}")
            cursor.execute(
                "SELECT iemid from stations where id = %s", (row["iem_id"],)
            )
        if cursor.rowcount != 1:
            LOG.info("IEMDB failure for %s", row["iem_id"])
            continue
        thrdf.at[idx, "iemid"] = cursor.fetchone()[0]


def fix_tracks_station(mesosite, row, thrdf):
    """Fix all the things."""
    cursor = mesosite.cursor()
    cursor.execute(
        "DELETE from station_attributes WHERE iemid = %s and "
        "attr = 'TRACKS_STATION'",
        (row["iemid"],),
    )
    # Ensure that the current thrdf is tracking
    cursor.execute(
        "SELECT iemid from station_attributes where attr = 'TRACKS_STATION' "
        "and value = %s",
        (row["tracks"],),
    )
    if cursor.rowcount == 0:
        for _idx, trow in thrdf.iterrows():
            if trow["period"].find("12/2021") == -1 or pd.isna(trow["iemid"]):
                continue
            LOG.info(
                "Adding TRACKS_STATION entry %s -> %s",
                trow["iemid"],
                row["tracks"],
            )
            cursor.execute(
                "INSERT into station_attributes(iemid, attr, value) "
                "VALUES (%s, 'TRACKS_STATION', %s)",
                (trow["iemid"], row["tracks"]),
            )
            break

    cursor.close()
    mesosite.commit()


def add_threading(mesosite, row, thrdf):
    """Add threading info."""
    cursor = mesosite.cursor()
    for _idx, trow in thrdf.iterrows():
        if pd.isna(trow["iemid"]):
            continue
        # Convert period into dates
        text = trow["period"].strip()
        if text.find(" to ") == -1:
            continue
        sdate, edate = text.split(" to ")
        sdate = sdate.replace("//", "/")
        if edate == "12/2021":
            edate = None
        if len(sdate) in (6, 7):
            sdate = datetime.datetime.strptime(f"01/{sdate}", "%d/%m/%Y")
        else:
            sdate = datetime.datetime.strptime(sdate, "%m/%d/%Y")
        if edate is None:
            pass
        elif len(edate) in (6, 7):
            edate = datetime.datetime.strptime(f"01/{edate}", "%d/%m/%Y")
            edate += datetime.timedelta(days=35)
            edate = edate.replace(day=1)
            edate -= datetime.timedelta(days=1)
        else:
            edate = datetime.datetime.strptime(edate, "%m/%d/%Y")
        LOG.info(
            "Add thread %s %s %s %s", row["iemid"], trow["iemid"], sdate, edate
        )
        cursor.execute(
            "INSERT into station_threading(iemid, source_iemid, begin_date, "
            "end_date) values(%s, %s, %s, %s)",
            (row["iemid"], trow["iemid"], sdate, edate),
        )

    cursor.close()
    mesosite.commit()


def main():
    """Go Main Go."""
    req = requests.get(
        "https://threadex.rcc-acis.org/data/threads_dict.json",
        timeout=60,
    )
    threadinfo = req.json()
    mesosite = get_dbconn("mesosite")

    df = find_candidates()
    for station, row in df.iterrows():
        # See what ACIS says for this treaded station
        thrdf = get_threading_info(threadinfo, station)
        if thrdf is None:
            LOG.info("Failed to thread %s", station)
            continue
        # Check that we have station info for these IDs
        check_and_add(mesosite, thrdf)
        # Remove TRACKS_STATION attribute
        fix_tracks_station(mesosite, row, thrdf)
        # Add threading info
        add_threading(mesosite, row, thrdf)


if __name__ == "__main__":
    main()
