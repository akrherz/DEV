"""More precise timing.

Whilst the database does track emergencies, it does not explicitly list when
an event came in and out of emergency status.  We shall try that here."""

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.nws.products.vtec import parser
from pyiem.util import get_dbconn

FFE = "FLASH FLOOD EMERGENCY"
BASE = "https://mesonet.agron.iastate.edu/p.php"


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        "WITH data as ("
        "SELECT wfo, eventid, issue at time zone 'UTC' as issue, report, "
        "expire at time zone 'UTC' as expire, "
        "svs, row_number() OVER (PARTITION by wfo, eventid, "
        "extract(year from issue) ORDER by length(svs) DESC) from "
        "warnings where phenomena = 'FF' and significance = 'W' and "
        "is_emergency) "
        "SELECT * from data WHERE row_number = 1 ORDER by issue, wfo, eventid",
        pgconn,
        index_col=None,
    )
    rows = []
    for _i, row in df.iterrows():
        v = parser(row["report"])
        report = row["report"].replace("\r\r\n", " ").replace("\n", " ")
        first = None
        last = None
        links = []
        if report.find(FFE) > -1:
            first = row["issue"]
            last = row["issue"]
            links.append(f"{BASE}?pid={v.get_product_id()}")
        for prod in ("" if row["svs"] is None else row["svs"]).split("__"):
            if prod.strip() == "":
                continue
            v = parser(prod)
            links.append(f"{BASE}?pid={v.get_product_id()}")
            if prod.replace("\r\r\n", " ").replace("\n", " ").find(FFE) > -1:
                if first is None:
                    first = v.valid.replace(tzinfo=None)
                last = v.valid.replace(tzinfo=None)
        rows.append(
            {
                "year": row["issue"].year,
                "wfo": row["wfo"],
                "eventid": row["eventid"],
                "first_mention": first,
                "last_mention": last,
                "issue": row["issue"],
                "expire": row["expire"],
                "links": " ".join(links),
            }
        )

    df = pd.DataFrame(rows)
    df["delta_mention_minutes"] = (
        df["last_mention"] - df["first_mention"]
    ).dt.total_seconds() / 60
    df["delta_issue_expire_minutes"] = (
        df["expire"] - df["issue"]
    ).dt.total_seconds() / 60
    df.to_csv("FFE_times.csv", index=False)


if __name__ == "__main__":
    main()
