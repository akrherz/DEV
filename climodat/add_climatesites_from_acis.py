"""Review what ACIS says for potential climate sites."""
# stdlib
import sys
from datetime import date, datetime, timedelta

# Third Party
import requests

from pyiem.network import Table as NetworkTable
from pyiem.reference import nwsli2state
from pyiem.util import convert_value, get_dbconn, logger

LOG = logger()
state2nwsli = dict((value, key) for key, value in nwsli2state.items())


def make_dates(tokens):
    """Convert to dates."""
    if not tokens:
        return date(2000, 1, 1), date(2000, 1, 1)
    fmt = "%Y-%m-%d"
    return datetime.strptime(tokens[0], fmt), datetime.strptime(tokens[1], fmt)


def process_state(state, data):
    """Do Some Magic."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    COOP_SITES = NetworkTable(f"{state}_COOP", only_online=False)
    DCP_SITES = NetworkTable(f"{state}_DCP", only_online=False)
    CLIMATE_SITES = NetworkTable(f"{state}CLIMATE", only_online=False)
    added = []
    known = 0
    dups = 0
    for meta in data["meta"]:
        coops = [s.split()[0] for s in meta["sids"] if s.find(" 7") > -1]
        acis_sids = [s.split()[0] for s in meta["sids"] if s.endswith(" 2")]
        if not acis_sids:
            # LOG.info("failed to get 2-type station for %s", meta["sids"])
            continue
        # Check for duplicate listed stations
        for sid in acis_sids:
            if sid in added:
                dups += 1
                LOG.info("Skipping %s as redundant station id", sid)
                continue
        acis = acis_sids[0]
        if len(acis_sids) > 1:
            LOG.info("Duplicated 2-type IDs %s, %s", acis_sids, meta["name"])
            for _acis in acis_sids:
                lookup = state + _acis[-4:]
                if lookup in CLIMATE_SITES.sts:
                    acis = _acis
        if len(acis) != 6:
            LOG.info("ACIS id %s not len=6 %s", acis, meta["sids"])
            continue
        clstation = state + acis[-4:]
        # We already know about this site
        if clstation in CLIMATE_SITES.sts:
            known += 1
            continue
        (maxt, pcpn) = [make_dates(r) for r in meta["valid_daterange"]]
        if (maxt[1] - maxt[0]) < timedelta(days=365) and (
            pcpn[1] - pcpn[0]
        ) < timedelta(days=365):
            LOG.info("Skipping %s with too little data", clstation)
            continue
        nwsli = None
        if len(coops) > 1:
            LOG.info("Duplicated coops %s %s", meta["sids"], meta["name"])
            for _nwsli in coops:
                if _nwsli in COOP_SITES.sts:
                    nwsli = _nwsli
        elif coops:
            nwsli = coops[0]
        # This station is online if temp or precip last date is this year
        online = date.today().year in [maxt[1].year, pcpn[1].year]
        tracking = None
        if online and nwsli is not None:
            if nwsli in COOP_SITES.sts:
                tracking = f"{nwsli}|{state}_COOP"
            elif nwsli in DCP_SITES.sts:
                LOG.info("Ignoring %s as tracks %s[DCP]", clstation, nwsli)
                continue
            else:
                tracking = f"{nwsli}|{state}_COOP"
                LOG.info("--------- Adding COOP %s", nwsli)
                cursor.execute(
                    "INSERT into stations(id, name, network, country, state, "
                    "plot_name, online, metasite, geom, elevation) VALUES "
                    "(%s, %s, %s, %s, %s, %s, %s, 't', "
                    "'SRID=4326;POINT(%s %s)', %s) "
                    "RETURNING iemid",
                    (
                        nwsli,
                        meta["name"],
                        f"{state}_COOP",
                        "US",
                        state,
                        meta["name"],
                        online,
                        meta["ll"][0],
                        meta["ll"][1],
                        convert_value(meta.get("elev", -999), "feet", "meter"),
                    ),
                )
        if online and tracking is None:
            LOG.info(
                "skipping add for online %s without station: %s",
                clstation,
                meta,
            )
            continue
        LOG.info("Add %s online: %s %s", clstation, online, tracking)
        CLIMATE_SITES.sts[clstation] = {}
        added.append(acis)
        cursor.execute(
            "INSERT into stations(id, name, network, country, state, "
            "plot_name, online, metasite, geom, elevation) VALUES "
            "(%s, %s, %s, %s, %s, %s, %s, 't', 'SRID=4326;POINT(%s %s)', %s) "
            "RETURNING iemid",
            (
                clstation,
                meta["name"],
                f"{state}CLIMATE",
                "US",
                state,
                meta["name"],
                online,
                meta["ll"][0],
                meta["ll"][1],
                convert_value(meta.get("elev", -999), "feet", "meter"),
            ),
        )
        iemid = cursor.fetchone()[0]
        # setup the tracking attribute
        if tracking:
            cursor.execute(
                "INSERT into station_attributes(iemid, attr, value) "
                "VALUES (%s, %s, %s)",
                (iemid, "TRACKS_STATION", tracking),
            )

    cursor.close()
    pgconn.commit()
    LOG.info("Added: %s Known: %s Dups: %s", len(added), known, dups)


def main(argv):
    """Go Main Go."""
    state = argv[1]
    req = requests.post(
        "http://data.rcc-acis.org/StnMeta",
        json={
            "meta": "valid_daterange,sids,name,ll,elev",
            "elems": "maxt,pcpn",
            "state": state,
        },
        timeout=60,
    )
    data = req.json()
    if "meta" not in data:
        LOG.info("Got status_code %s with no meta", req.status_code)
        LOG.info(req.content)
        return
    process_state(state, data)


if __name__ == "__main__":
    main(sys.argv)
