"""Review what ACIS says for unknown NWSLIs."""

# Third Party
import requests

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, get_sqlalchemy_conn, logger

LOG = logger()


def process(nwsli, row, data):
    """Do Some Magic."""
    dbconn = get_dbconn("mesosite")
    cursor = dbconn.cursor()
    for meta in data["meta"]:
        print("-------------------------------")
        print(nwsli)
        print(row["product"])
        print(meta["name"])
        print(meta["state"])
        print(meta.get("network"))
    meta = data["meta"][0]
    res = input(f"Enter City [{meta['name']}]: ")
    city = meta["name"] if res == "" else res
    network = input("Enter network: ")
    res = input("Enter Country [US]: ")
    country = res if res != "" else "US"
    cursor.execute(
        "INSERT into stations (id, name, network, country, plot_name, "
        "state, elevation, online, metasite, geom) VALUES (%s, %s, %s, "
        "%s, %s, %s, %s, %s, %s, 'SRID=4326;POINT(%s %s)')",
        (
            nwsli,
            city,
            network,
            country,
            city,
            meta["state"],
            -999,
            True,
            False,
            meta["ll"][0],
            meta["ll"][1],
        ),
    )
    cursor.close()
    dbconn.commit()


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("hads") as conn:
        df = read_sql(
            "SELECT nwsli, max(product) as product from unknown "
            "where length(nwsli) = 5 GROUP by nwsli ORDER by nwsli ASC",
            conn,
            index_col="nwsli",
        )
    LOG.info("Found %s unknown 5-char ids", len(df.index))
    for nwsli, row in df.iterrows():
        req = requests.post(
            "http://data.rcc-acis.org/StnMeta",
            json={
                "meta": "name,ll,elev,state,network",
                "sids": nwsli,
            },
            timeout=60,
        )
        data = req.json()
        if "meta" not in data or not data["meta"]:
            LOG.info("status_code %s no meta %s", req.status_code, nwsli)
            LOG.info(req.content)
            continue
        process(nwsli, row, data)


if __name__ == "__main__":
    main()
