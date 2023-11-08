"""Dump something."""
# Local
import sys

import pandas as pd

# Third Party
from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go."""
    threshold = float(argv[1])
    df = pd.read_sql(
        "SELECT station, year, month, "
        "sum(case when precip >= %s then 1 else 0 end) as days from "
        "alldata where substr(station, 3, 1) = 'C' "
        "GROUP by station, year, month "
        "ORDER by station ASC, year ASC, month ASC",
        get_dbconn("coop"),
        params=(threshold,),
        index_col=None,
    )
    df["colname"] = df["year"].astype(str) + "_" + df["month"].astype(str)
    df = df.drop(["year", "month"], axis=1).pivot(
        index="station", columns="colname", values="days"
    )
    df.to_csv(f"clidistrict_{threshold:.2f}inch.csv")


if __name__ == "__main__":
    main(sys.argv)
