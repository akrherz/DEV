"""Compute bias of avg_rh."""
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql
from metpy.calc import relative_humidity_from_dewpoint
from metpy.units import units


def main():
    """Go Main Go."""
    pgconn = get_dbconn("iem")
    df = read_sql(
        """
        SELECT day, max_tmpf, min_tmpf, avg_rh,
        extract(month from day) as month,
        extract(year from day) as year from summary
        WHERe iemid = 37004 ORDER by day
    """,
        pgconn,
    )
    df["est_rh"] = (
        relative_humidity_from_dewpoint(
            df["max_tmpf"].values * units.degF,
            df["min_tmpf"].values * units.degF,
        )
        .to(units.percent)
        .m
    )
    df["bias"] = df["est_rh"] - df["avg_rh"]
    print(df.groupby("month").mean())


if __name__ == "__main__":
    main()
