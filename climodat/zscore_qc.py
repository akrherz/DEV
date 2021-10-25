"""Use a simple zscore system to null out suspect data"""
import sys

from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def do(state, vname):
    """do"""
    pgconn = get_dbconn("coop")
    network = f"{state}CLIMATE"
    df = read_sql(
        f"""
    WITH mystations as (
    SELECT id from stations where network = %s and
    (temp24_hour is null or temp24_hour between 4 and 9) and
    substr(id, 3, 1) != 'C' and substr(id, 3, 4) != '0000'),
    stats as (
    SELECT day, avg({vname}), stddev({vname}) from alldata_{state} o
    JOIN mystations t on (o.station = t.id) GROUP by day),
    agg as (
    SELECT o.day, abs((o.{vname} - s.avg) / s.stddev) as zscore,
    o.{vname}, s.avg, s.stddev, o.station from alldata_{state} o,
    mystations t, stats s WHERE
    o.day = s.day and t.id = o.station)

    SELECT * from agg where zscore > 4 ORDER by day
    """,
        pgconn,
        params=(network,),
        index_col=None,
    )
    print(df.groupby("day").count())


def main(argv):
    """Go Main Go"""
    state = argv[1]
    for vname in ["high", "low"]:
        do(state, vname)


if __name__ == "__main__":
    main(sys.argv)
