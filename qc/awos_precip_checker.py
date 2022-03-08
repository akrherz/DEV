"""Simple comparison of totals."""
import sys
from datetime import date

import requests
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_sqlalchemy_conn
from sqlalchemy import text

SITES = ("PRO", "BNW", "IKV", "GGI")


def main(argv):
    """Go Main Go."""
    dt = date(int(argv[1]), int(argv[2]), int(argv[3]))
    with get_sqlalchemy_conn("iem") as conn:
        obs = read_sql(
            text(
                "SELECT id, st_x(geom) as lon, st_y(geom) as lat, pday from "
                "summary s JOIN stations t on (s.iemid = t.iemid) "
                "WHERE t.network = 'AWOS' and "
                "id in :ids and day = :dt ORDER by id"
            ),
            conn,
            params={"ids": SITES, "dt": dt},
            index_col="id",
        )
    obs["prism"] = -1.0
    obs["mrms"] = -1.0
    obs["iemre"] = -1.0
    for sid, row in obs.iterrows():
        r = requests.get(
            f"https://mesonet.agron.iastate.edu/iemre/daily/{dt:%Y-%m-%d}/"
            f"/{row['lat']}/{row['lon']}/json"
        )
        data = r.json()
        iemre = pd.DataFrame(data["data"])
        print(
            f"{sid} ob:{row['pday']} iemre: {iemre['daily_precip_in'].sum()}"
        )


if __name__ == "__main__":
    main(sys.argv)
