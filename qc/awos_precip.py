"""Simple comparison of totals."""
import sys

import requests
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go."""
    year = argv[1]
    obs = read_sql(
        "SELECT id, st_x(geom) as lon, st_y(geom) as lat, sum(pday) from "
        "summary_2015 s "
        "JOIN stations t on (s.iemid = t.iemid) WHERE t.network = 'AWOS' and "
        "pday > 0 GROUP by id, lon, lat ORDER by id",
        get_dbconn("iem"),
        index_col="id",
    )
    obs["prism"] = -1.0
    obs["mrms"] = -1.0
    obs["iemre"] = -1.0
    for sid, row in obs.iterrows():
        r = requests.get(
            f"https://mesonet.agron.iastate.edu/iemre/multiday/{year}-01-01/"
            f"{year}-12-31/{row['lat']}/{row['lon']}/json"
        )
        data = r.json()
        iemre = pd.DataFrame(data["data"])
        obs.at[sid, "prism"] = iemre["prism_precip_in"].sum()
        obs.at[sid, "mrms"] = iemre["mrms_precip_in"].sum()
        obs.at[sid, "iemre"] = iemre["daily_precip_in"].sum()

    obs.to_csv(f"awos_precip_{year}.csv")


if __name__ == "__main__":
    main(sys.argv)
