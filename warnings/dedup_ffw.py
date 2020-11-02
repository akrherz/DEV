"""see akrherz/iem#191

Dedup some duplicated FFWs in the warnings table."""
from datetime import timezone
import sys

from pyiem.util import get_dbconn, noaaport_text
from pyiem.nws.product import TextProduct
from pandas.io.sql import read_sql


def dedup(pgconn, cursor, row):
    """Figure out if we can eliminate the bad entry :/"""
    # Compute which events are at play.
    df = read_sql(
        f"SELECT issue, expire, report, ctid from warnings_{row['year']} "
        "WHERE phenomena = %s and significance = %s and expire = %s and "
        "ugc = %s",
        pgconn,
        params=(
            row["phenomena"],
            row["significance"],
            row["expire"],
            row["ugc"],
        ),
    )
    for i, row2 in df.iterrows():
        utcnow = row2["issue"].astimezone(timezone.utc)
        tp = TextProduct(row2["report"], utcnow=utcnow)
        delta = (tp.valid - utcnow).total_seconds()
        if delta > 1800:
            print("NOOP")
            continue
        print(f"{row2['ctid']} {utcnow} -> {tp.valid}")


def main(argv):
    """Go for this year."""
    year = int(argv[1])
    phenomena = argv[2]
    significance = argv[3]
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    # Candidates have duplicated expire times and issue timestamps that are
    # slightly off due to changes in how I assign product valid timestamps.
    df = read_sql(
        "SELECT ugc, expire, min(issue) as min_issue, "
        f"max(issue) as max_issue, count(*) from warnings_{year} WHERE "
        "phenomena = %s and significance = %s "
        "GROUP by ugc, expire HAVING count(*) > 1",
        pgconn,
        index_col=None,
        params=(phenomena, significance),
    )
    df["year"] = year
    df["phenomena"] = phenomena
    df["significance"] = significance
    print("%s entries for dedup found" % (len(df.index),))
    for _, row in df.iterrows():
        delta = (row["max_issue"] - row["min_issue"]).total_seconds()
        if abs(delta) > 1800:
            print(f"skipping {row}")
            continue
        print(
            "  %s %s %s is a dup"
            % (row["ugc"], row["min_issue"], row["max_issue"])
        )
        dedup(pgconn, cursor, row)

    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
