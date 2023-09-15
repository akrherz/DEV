"""A util script to dump IEMRE json service to csv files"""

import requests

import pandas as pd
from pyiem.util import get_sqlalchemy_conn


def workflow(gid, lat, lon):
    """Do Some Work Please"""
    res = []
    for year in range(2010, 2016):
        print("Processing GID: %s year: %s" % (gid, year))
        uri = (
            "http://mesonet.agron.iastate.edu/iemre/multiday/"
            "%s-01-01/%s-12-31/%s/%s/json"
        ) % (year, year, lat, lon)
        req = requests.get(uri, timeout=30)
        for row in req.json()["data"]:
            res.append(row)
    df = pd.DataFrame(res)
    df.to_csv("%s.csv" % (gid,), index=False)


def main():
    """Go Main Go"""
    df = pd.read_excel("/tmp/dates.xlsx")
    df["high_temp_f"] = 0
    df["low_temp_f"] = 0
    with get_sqlalchemy_conn("postgis") as pgconn:
        counties = pd.read_sql(
            "SELECT name, ST_x(centroid) as lon, st_y(centroid) as lat from "
            "ugcs where end_ts is null and substr(ugc, 1, 3) = 'IAC' "
            "ORDER by name ASC",
            pgconn,
        )
    for idx, row in df.iterrows():
        df2 = counties[counties["name"] == row["Site"]]
        uri = (
            "http://mesonet.agron.iastate.edu/iemre/daily/"
            f"{row['Date'].strftime('%Y-%m-%d')}/"
            f"{df2.iloc[0]['lat']}/{df2.iloc[0]['lon']}/json"
        )
        req = requests.get(uri)
        data = req.json()["data"][0]
        df.at[idx, "high_temp_f"] = data["daily_high_f"]
        df.at[idx, "high_low_f"] = data["daily_low_f"]

    df.to_csv("/tmp/dates.csv")


if __name__ == "__main__":
    main()
