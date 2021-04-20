"""Review what ACIS says for potential climate sites."""
# stdlib
from datetime import datetime
import sys

# Third Party
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger
from pyiem.reference import nwsli2state
import requests

LOG = logger()
state2nwsli = dict([(value, key) for key, value in nwsli2state.items()])


def make_dates(tokens):
    """Convert to dates."""
    if not tokens:
        return None
    fmt = "%Y-%m-%d"
    return datetime.strptime(tokens[0], fmt), datetime.strptime(tokens[1], fmt)


def process_state(state, data):
    """Do Some Magic."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    COOP_SITES = NetworkTable(f"{state}_COOP", only_online=False)
    CLIMATE_SITES = NetworkTable(f"{state}CLIMATE", only_online=False)
    cmds = []
    unknown_coops = []
    for meta in data["meta"]:
        sids = [
            s.split()[0]
            for s in meta["sids"]
            if s.find(f"{state2nwsli[state]} 7") > -1
        ]
        if not sids or len(sids) > 1:
            continue
        acis_sid = [s.split()[0] for s in meta["sids"] if s.endswith(" 2")]
        if not acis_sid:
            LOG.info("failed to get 2-type station for %s", meta["sids"])
            continue
        acis_sid = acis_sid[0]
        nwsli = sids[0]
        (maxt, pcpn, snow) = [make_dates(r) for r in meta["valid_daterange"]]
        if None in [maxt, pcpn, snow]:
            continue
        # We want sites having 2021 data and data before 1970
        if not all([t[1].year == 2021 for t in [maxt, pcpn, snow]]):
            continue
        if not all([t[0].year < 1970 for t in [maxt, pcpn, snow]]):
            continue
        if nwsli not in COOP_SITES.sts:
            print(f"Whoa {nwsli} is not a known COOP site?")
            unknown_coops.append(nwsli)
            continue
        # Here we go!
        clstation = (
            state
            + [s.split()[0][-4:] for s in meta["sids"] if s.find(" 2") > -1][0]
        )
        if clstation in CLIMATE_SITES.sts:
            tracks = CLIMATE_SITES.sts[clstation]["attributes"].get(
                "TRACKS_STATION"
            )
            if tracks is None:
                iemid = CLIMATE_SITES.sts[clstation]["iemid"]
                print(f"{clstation} should track {nwsli}")
                cursor.execute(
                    "INSERT into station_attributes(iemid, attr, value) "
                    "VALUES (%s, %s, %s)",
                    (iemid, "TRACKS_STATION", f"{nwsli}|{state}_COOP"),
                )
            if not CLIMATE_SITES.sts[clstation]["online"]:
                print(f"Setting {clstation} to online")
                cursor.execute(
                    "UPDATE stations SET online = 't' where iemid = %s",
                    (iemid,),
                )
            print(f"Skipping {clstation} -> {tracks} as already known.")
            continue
        entry = COOP_SITES.sts[nwsli]
        print(f"--> creating {clstation} {entry['name']} {nwsli}")
        cursor.execute(
            "INSERT into stations(id, name, network, country, state, "
            "plot_name, elevation, online, metasite, geom) VALUES "
            "(%s, %s, %s, %s, %s, %s, %s, 't', 't', 'SRID=4326;POINT(%s %s)') "
            "RETURNING iemid",
            (
                clstation,
                entry["name"],
                f"{state}CLIMATE",
                "US",
                state,
                entry["name"],
                entry["elevation"],
                entry["lon"],
                entry["lat"],
            ),
        )
        iemid = cursor.fetchone()[0]
        # setup the tracking attribute
        cursor.execute(
            "INSERT into station_attributes(iemid, attr, value) "
            "VALUES (%s, %s, %s)",
            (iemid, "TRACKS_STATION", f"{nwsli}|{state}_COOP"),
        )
        cmds.append(f"python use_acis.py {clstation} {acis_sid}")

    cursor.close()
    pgconn.commit()
    print()
    print(unknown_coops)
    print()
    print("\n".join(cmds))


def main(argv):
    """Go Main Go."""
    state = argv[1]
    req = requests.post(
        "http://data.rcc-acis.org/StnMeta",
        json={
            "meta": "valid_daterange,sids",
            "elems": "maxt,pcpn,snow",
            "state": state,
        },
    )
    data = req.json()
    if "meta" not in data:
        LOG.info("Got status_code %s with no meta", req.status_code)
        LOG.info(req.content)
        return
    process_state(state, data)


if __name__ == "__main__":
    main(sys.argv)
