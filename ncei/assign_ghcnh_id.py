"""Set a station attribute GHCNH_ID."""

from typing import Optional

import click
import httpx
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()


def query_icao(icao: str) -> Optional[str]:
    """A two step NCEI HOMR process to figure out the GHCNH_ID."""

    resp = httpx.get(
        "https://www.ncei.noaa.gov/access/homr/services/station/search?"
        f"date=all&headersOnly=true&qid=ICAO:{icao}",
        timeout=60,
    )
    if resp.status_code != 200:
        return None
    stations = resp.json()["stationCollection"]["stations"]
    found = []
    for meta in stations:
        ncei_id = meta["ncdcStnId"]
        resp = httpx.get(
            "https://www.ncei.noaa.gov/"
            f"access/homr/services/station/{ncei_id}?date=all",
            timeout=60,
        )
        stations2 = resp.json()["stationCollection"]["stations"]
        for meta2 in stations2:
            for ident in meta2["identifiers"]:
                if ident["idType"] == "GHCNH":
                    if ident["id"] in found:
                        continue
                    if ident["date"]["endDate"] == "Present":
                        found.append(ident["id"])
                    else:
                        LOG.info(
                            "Ignoring not-current %s for %s", ident["id"], icao
                        )
    if len(found) == 1:
        return found[0]
    return None


@click.command()
@click.option("--network", default="IA_ASOS", help="Network to query")
def main(network: str):
    """Go Main Go."""
    nt = NetworkTable(network, only_online=False)
    with get_sqlalchemy_conn("mesosite") as conn:
        for sid, meta in nt.sts.items():
            icao = sid if len(sid) == 4 else f"K{sid}"
            if meta["attributes"].get("GHCNH_ID") is not None:
                continue
            res = query_icao(icao)
            if res is None:
                print(f"Failed to find {sid}")
                continue
            print(f"{sid} -> {res}")
            conn.execute(
                sql_helper(
                    "insert into station_attributes(iemid, attr, value) "
                    "values (:iemid, 'GHCNH_ID', :ghcnid) "
                ),
                {"iemid": meta["iemid"], "ghcnid": res},
            )
            conn.commit()


if __name__ == "__main__":
    main()
