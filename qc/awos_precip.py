"""Simple comparison of totals."""

import sys

import requests

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_sqlalchemy_conn


def main(argv):
    """Go Main Go."""
    year = argv[1]
    with get_sqlalchemy_conn("iem") as conn:
        obs = read_sql(
            "SELECT id, st_x(geom) as lon, st_y(geom) as lat, sum(pday) from "
            f"summary_{year} s "
            "JOIN stations t on (s.iemid = t.iemid) WHERE "
            "t.network = 'IA_ASOS' "
            "and pday > 0 and extract(month from day) > 3 "
            "GROUP by id, lon, lat ORDER by id",
            conn,
            index_col="id",
        )
    obs["prism"] = -1.0
    obs["mrms"] = -1.0
    obs["iemre"] = -1.0
    for sid, row in obs.iterrows():
        r = requests.get(
            f"https://mesonet.agron.iastate.edu/iemre/multiday/{year}-04-01/"
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
