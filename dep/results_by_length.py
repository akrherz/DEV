"""Debug our flowpath length fun."""
import sys

from pyiem.util import get_dbconn
from pyiem.dep import read_env
import pandas as pd
from pandas.io.sql import read_sql


def main(argv):
    """Go Main Go."""
    huc12 = argv[1]
    pgconn = get_dbconn("idep")
    df = read_sql(
        """
        SELECT fpath, st_length(geom) from flowpaths where scenario = 0
        and huc_12 = %s ORDER by st_length ASC
    """,
        pgconn,
        params=(huc12,),
        index_col="fpath",
    )
    df["delivery"] = 0.0
    df["loss"] = 0.0
    df["events"] = 0.0
    df["precip"] = 0.0
    sts = pd.Timestamp(year=2008, day=1, month=1)
    ets = pd.Timestamp(year=2019, day=1, month=1)
    for fpath, row in df.iterrows():
        res = read_env(
            "/i/0/env/%s/%s/%s_%s.env" % (huc12[:8], huc12[8:], huc12, fpath)
        )
        res["delivery"] = res["sed_del"] / row["st_length"]
        df2 = res[(res["date"] > sts) & (res["date"] < ets)]
        df.at[fpath, "delivery"] = df2["delivery"].sum() * 4.463
        df.at[fpath, "loss"] = df2["av_det"].sum() * 4.463
        df.at[fpath, "events"] = df2["delivery"].count()
        df.at[fpath, "precip"] = df2["precip"].sum() / 25.4
    print(df)
    baseline = df["delivery"].mean() / 11.0
    for length in range(0, 100, 5):
        df2 = df[df["st_length"] > length]
        val = df2["delivery"].mean() / 11.0
        print("%3i %.2f %4.2f" % (length, val, val / baseline))


if __name__ == "__main__":
    main(sys.argv)
