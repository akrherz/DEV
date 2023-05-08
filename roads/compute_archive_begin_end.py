"""Figure out what our time domain is for our segments."""

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, get_sqlalchemy_conn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    with get_sqlalchemy_conn("postgis") as conn:
        base = read_sql(
            "select segid, archive_begin, archive_end from roads_base",
            conn,
            index_col="segid",
        )
    for year in range(2018, 2022):
        table = f"roads_{year}_{year + 1}_log"
        with get_sqlalchemy_conn("postgis") as conn:
            df = read_sql(
                f"SELECT segid, min(valid), max(valid) from {table} "
                "WHERE valid is not null GROUP by segid",
                conn,
                index_col="segid",
            )
        for segid, row in df.iterrows():
            curmin = base.at[segid, "archive_begin"]
            curmax = base.at[segid, "archive_end"]
            if curmin is None or row["min"] < curmin:
                base.at[segid, "archive_begin"] = row["min"]
            if curmax is None or row["max"] > curmax:
                base.at[segid, "archive_end"] = row["max"]

    cursor = pgconn.cursor()
    for segid, row in base.iterrows():
        if pd.isnull(row["archive_begin"]) or pd.isnull(row["archive_end"]):
            continue
        print(f"{segid} {row['archive_begin']} -> {row['archive_end']}")
        cursor.execute(
            "update roads_base SET archive_begin = %s, archive_end = %s "
            "where segid = %s",
            (row["archive_begin"], row["archive_end"], segid),
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
