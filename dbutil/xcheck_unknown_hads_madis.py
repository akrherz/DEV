"""See if MADIS knows about unknown HADS sites..."""

import re

import pandas as pd
from pyiem.database import (
    get_sqlalchemy_conn,
    sql_helper,
    with_sqlalchemy_conn,
)
from pyiem.util import logger
from sqlalchemy.engine import Connection

NWSLI_RE = re.compile(r"^[A-Z]{4}[0-9]$")
US_STATE_RE = re.compile(r" ([A-Z]{2}) US ")
LOG = logger()
SRC = (
    "https://madis-data.cprk.ncep.noaa.gov/madisPublic1/data/"
    "stations/public_stntbl.txt"
)


@with_sqlalchemy_conn("mesosite")
def main(conn: Connection | None = None):
    """Go Main Go."""
    stationsdf = pd.read_table(
        SRC,
        sep="|",
        header=None,
        engine="python",
        names=[
            "sid",
            "dist",
            "elev",
            "lat",
            "lon",
            "shrug",
            "provider",
            "name",
        ],
        skipinitialspace=True,
        usecols=range(8),
    ).set_index("sid")
    LOG.info("Found %s MADIS stations", len(stationsdf.index))

    with get_sqlalchemy_conn("hads") as pgconn:
        unknown_hads = pd.read_sql(
            sql_helper("""
    with counts as (
        select station, count(*) from raw where valid > 'TODAY'
        group by station),
    agg as (
        select s.iemid, c.station, c.count from
        counts c LEFT JOIN stations s on (c.station = s.id))
    select * from agg where iemid is null order by count desc
                       """),
            pgconn,
            index_col="station",
        )
    LOG.info("Found %s unknown stations", len(unknown_hads.index))

    counts = {
        "unknown_unknowns": 0,
        "state_unknown": 0,
        "added": 0,
        "ambiguous_station": 0,
        "accounted_for_obs": 0,
    }
    sampling = 300
    LOG.info("Sampling %s rows just to be careful", sampling)
    for station, row in unknown_hads.head(sampling).iterrows():
        if station not in stationsdf.index:
            counts["unknown_unknowns"] += 1
            continue
        is_nwsli = NWSLI_RE.match(str(station))
        if is_nwsli:
            LOG.warning("NWSLIish %s is known to MADIS, do manual", station)
            continue
        # State column needs to exist
        meta = stationsdf.loc[[str(station)]]
        if len(meta.index) > 1:
            counts["ambiguous_station"] += 1
            continue
        meta = meta.iloc[0].to_dict()
        m = US_STATE_RE.findall(meta["name"])
        if not m:
            counts["state_unknown"] += 1
            continue
        state = m[0]
        # Add!
        name = meta["name"][:33].replace(station, "").strip()
        network = f"{state}_DCP"
        LOG.info("Adding %s[%s] `%s` ", station, network, name)
        counts["accounted_for_obs"] += row["count"]
        conn.execute(
            sql_helper(
                """
            INSERT INTO stations (id, network, name, state, country,
            plot_name, elevation, geom, online, metasite) VALUES (
            :sid, :network, :name, :state, 'US',
            :name, :elev, ST_Point(:lon, :lat, 4326), 't', 'f'
            )
            """
            ),
            {
                "sid": station,
                "name": name,
                "elev": meta["elev"],
                "lat": meta["lat"],
                "lon": meta["lon"],
                "network": network,
                "state": state,
            },
        )
        counts["added"] += 1
    conn.commit()
    LOG.info("Counts: %s", counts)


if __name__ == "__main__":
    main()
