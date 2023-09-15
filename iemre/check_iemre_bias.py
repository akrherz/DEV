"""Look to see if we have something systematic wrong with IEMRE"""
import json
import sys

import requests

import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_sqlalchemy_conn

COLS = ["ob_pday", "daily_precip_in", "precip_delta", "prism_precip_in"]


def main(argv):
    """Go Main Go"""
    station = argv[1]
    year = int(argv[2])
    nt = NetworkTable("IACLIMATE")

    with get_sqlalchemy_conn("coop") as pgconn:
        df = pd.read_sql(
            """
            SELECT day, precip, high, low from alldata WHERE station = %s and
            year = %s ORDER by day ASC
        """,
            pgconn,
            params=(station, year),
            index_col="day",
        )

    uri = (
        f"https://mesonet.agron.iastate.edu/iemre/multiday/{year}-01-01/"
        f"{year}-12-31/{nt.sts[station]['lat']:.2f}/"
        f"{nt.sts[station]['lon']:.2f}/json"
    )
    req = requests.get(uri, timeout=30)
    j = json.loads(req.content)

    idf = pd.DataFrame(j["data"])
    idf["day"] = pd.to_datetime(idf["date"])
    idf.set_index("day", inplace=True)

    idf["ob_high"] = df["high"]
    idf["ob_low"] = df["low"]
    idf["ob_pday"] = df["precip"]

    idf["high_delta"] = idf["ob_high"] - idf["daily_high_f"]
    idf["low_delta"] = idf["ob_low"] - idf["daily_low_f"]
    idf["precip_delta"] = idf["ob_pday"] - idf["daily_precip_in"]
    idf = idf.sort_values("precip_delta", ascending=True)

    print("IEMRE greater than Obs")
    print(idf[COLS].head())
    print("Obs greater than IEMRE")
    print(idf[COLS].tail())
    print("Largest Obs with IEMRE < 0.01")
    idf2 = idf[idf["daily_precip_in"] < 0.01]
    print(idf2[["ob_pday", "daily_precip_in", "precip_delta"]].tail())

    print("Monthly Totals")
    print(idf[COLS].groupby(pd.Grouper(freq="M")).sum())
    print("sum")
    print(idf[COLS].sum())


if __name__ == "__main__":
    main(sys.argv)
