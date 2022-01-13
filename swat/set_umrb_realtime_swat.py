"""Update database flag."""

import pandas as pd
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    df = pd.read_csv("match.csv")
    df["HUC12"] = df["HUC12"].astype(str).str.pad(12, "left", "0")
    pgconn = get_dbconn("idep")
    cursor = pgconn.cursor()
    for _i, row in df.iterrows():
        cursor.execute(
            "UPDATE wbd_huc12 SET umrb_realtime_swat = 't' WHERE huc12 = %s",
            (row["HUC12"],),
        )
        if cursor.rowcount != 1:
            print(f"Failed to update {row['HUC12']}")
            return
    pgconn.commit()


if __name__ == "__main__":
    main()
