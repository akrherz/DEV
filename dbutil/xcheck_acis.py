"""Review what ACIS says for unknown NWSLIs."""


# Third Party
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, logger, convert_value
import requests

LOG = logger()


def process(nwsli, row, data):
    """Do Some Magic."""
    for meta in data["meta"]:
        print("-------------------------------")
        print(nwsli)
        print(row["product"])
        print(meta["name"])
        print(meta["state"])
        print(meta.get("network"))
        print(meta["ll"][1])
        print(meta["ll"][0])
        print(convert_value(meta["elev"], "feet", "meter"))


def main():
    """Go Main Go."""
    df = read_sql(
        "SELECT nwsli, max(product) as product from unknown "
        "where length(nwsli) = 5 GROUP by nwsli ORDER by nwsli ASC",
        get_dbconn("hads"),
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
        )
        data = req.json()
        if "meta" not in data:
            LOG.info("Got status_code %s with no meta", req.status_code)
            LOG.info(req.content)
            continue
        process(nwsli, row, data)


if __name__ == "__main__":
    main()
