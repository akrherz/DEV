"""Print a HUC12 diagnostic."""

import click
import pandas as pd
from dailyerosion.io.wepp import read_env
from dailyerosion.reference import KG_M2_TO_TON_ACRE
from pyiem.database import get_sqlalchemy_conn
from sqlalchemy import text


@click.command()
@click.option("--huc12", type=str, help="HUC12 to process", required=True)
@click.option("--year", type=int, help="Year to process", required=True)
def main(huc12, year):
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        df = pd.read_sql(
            text("""
            SELECT fpath, st_length(geom) from flowpaths where scenario = 0
            and huc_12 = :huc12 ORDER by st_length ASC
        """),
            conn,
            params={"huc12": huc12},
            index_col="fpath",
        )
    df["delivery"] = 0.0
    df["loss"] = 0.0
    df["events"] = 0.0
    df["precip"] = 0.0
    sts = pd.Timestamp(year=year, month=1, day=1)
    ets = pd.Timestamp(year=year, month=12, day=31)
    for fpath, row in df.iterrows():
        res = read_env(f"/i/0/env/{huc12[:8]}/{huc12[8:]}/{huc12}_{fpath}.env")
        res["delivery"] = res["sed_del"] / row["st_length"]
        df2 = res[(res["date"] > sts) & (res["date"] < ets)]
        df.at[fpath, "delivery"] = df2["delivery"].sum() * KG_M2_TO_TON_ACRE
        df.at[fpath, "loss"] = df2["av_det"].sum() * KG_M2_TO_TON_ACRE
        df.at[fpath, "events"] = df2["delivery"].count()
        df.at[fpath, "precip"] = df2["precip"].sum() / 25.4
    print(df["delivery"].describe())


if __name__ == "__main__":
    main()
