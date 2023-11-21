"""Some AWOSes are reporting 6 hour max/min, lets check that out!"""
import datetime
import sys

import pandas as pd
from pyiem.database import get_sqlalchemy_conn


def main(argv):
    """xref."""
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
            select valid at time zone 'UTC' as utc_valid, tmpf, max_tmpf_6hr,
            min_tmpf_6hr from t2023 where station = %s and
            valid > '2023-10-01' ORDER by valid ASC
            """,
            conn,
            params=(argv[1],),
            index_col="utc_valid",
            parse_dates="utc_valid",
        )
    for valid, row in df[df["max_tmpf_6hr"].notna()].iterrows():
        df2 = df.loc[valid - datetime.timedelta(hours=6) : valid]
        print(row["max_tmpf_6hr"], df2["tmpf"].max())


if __name__ == "__main__":
    main(sys.argv)
