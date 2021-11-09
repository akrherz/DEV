"""Simple comparison of totals."""

import requests
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    obs = read_sql(
        "SELECT id, st_x(geom) as lon, st_y(geom) as lat, sum(pday) from "
        "summary_2021 s "
        "JOIN stations t on (s.iemid = t.iemid) WHERE t.network = 'AWOS' and "
        "s.day >= '2021-04-01' and pday > 0 GROUP by id, lon, lat ORDER by id",
        get_dbconn("iem"),
        index_col="id",
    )
    obs["prism"] = -1.0
    obs["mrms"] = -1.0
    obs["iemre"] = -1.0
    for sid, row in obs.iterrows():
        r = requests.get(
            "https://mesonet.agron.iastate.edu/iemre/multiday/2021-04-01/"
            f"2021-11-09/{row['lat']}/{row['lon']}/json"
        )
        data = r.json()
        iemre = pd.DataFrame(data["data"])
        obs.at[sid, "prism"] = iemre["prism_precip_in"].sum()
        obs.at[sid, "mrms"] = iemre["mrms_precip_in"].sum()
        obs.at[sid, "iemre"] = iemre["daily_precip_in"].sum()

    obs.to_csv("awos_precip.csv")


if __name__ == "__main__":
    main()
