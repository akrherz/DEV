"""We Play."""

import pytz
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("asos")
    df = read_sql(
        """
    SELECT valid at time zone 'UTC' as valid2 from alldata LIMIT 10
    """,
        pgconn,
        index_col=None,
    )
    df["valid2"] = df["valid2"].dt.tz_localize(pytz.UTC)
    df["valid"] = df["valid2"].dt.tz_convert(pytz.timezone("America/Chicago"))
    print(df)


if __name__ == "__main__":
    main()
