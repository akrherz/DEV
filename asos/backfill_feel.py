"""Fill in the feel, relh columns."""

from datetime import datetime, timedelta

import click
import metpy.calc as mcalc
import numpy as np
import pandas as pd
from metpy.units import units
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.util import utc
from tqdm import tqdm

pd.set_option("future.no_silent_downcasting", True)


def bnds_check(val, low, high):
    """Check bounds."""
    if pd.isnull(val):
        return None
    if val < low:
        return None
    if val > high:
        return None
    return float(val)


def is_new(val, old):
    """Is this a new value."""
    if pd.isnull(val):
        return False
    if pd.isnull(old):
        return True
    return abs(val - old) > 0.01


@click.command()
@click.option(
    "--date",
    "dt",
    type=click.DateTime(),
    help="Date to process",
    required=True,
)
@click.option(
    "--dbname",
    default="asos",
    help="Database name to connect to",
)
def main(dt: datetime, dbname: str) -> None:
    """Go Main Go."""
    start_time = utc()
    sts = utc(dt.year, dt.month, dt.day)
    ets = sts + timedelta(hours=24)
    pgconn = get_dbconn(dbname)
    with get_sqlalchemy_conn(dbname) as conn:
        df = pd.read_sql(
            sql_helper(
                """
        SELECT station, valid, tmpf, dwpf, sknt, relh, feel,
        relh as old_relh, feel as old_feel from {table}
        WHERE valid >= :sts and valid < :ets and tmpf >= dwpf
        and (feel is null or relh is null)
        """,
                table=f"t{sts.year}",
            ),
            conn,
            params={"sts": sts, "ets": ets},
            index_col=None,
        )
    print(
        f"{sts:%Y%m%d} query of {len(df.index)} rows finished in "
        f"{(utc() - start_time).total_seconds():.4f}s"
    )
    start_time = utc()
    df["dirty"] = False
    df2 = df.fillna(np.nan)[pd.isnull(df["relh"])]
    if not df2.empty:
        print(f"Computing relh for {len(df2.index)} rows")
        df.loc[df2.index, "relh"] = (
            mcalc.relative_humidity_from_dewpoint(
                df2["tmpf"].values * units.degF,
                df2["dwpf"].values * units.degF,
            )
            .to(units.percent)
            .magnitude
        )
        df.loc[df2.index, "dirty"] = True
    df2 = df.fillna(np.nan)[pd.isnull(df["feel"]) & (df["relh"] > 0)]
    if not df2.empty:
        print(f"Computing feel for {len(df2.index)} rows")
        df.loc[df2.index, "feel"] = (
            mcalc.apparent_temperature(
                df2["tmpf"].values * units.degF,
                df2["relh"].values * units.percent,
                df2["sknt"].values * units.knots,
                mask_undefined=False,
            )
            .to(units.degF)
            .magnitude
        )
        df.loc[df2.index, "dirty"] = True
    cursor = pgconn.cursor()
    count = 0
    skips = 0
    for _, row in tqdm(df[df["dirty"]].iterrows(), total=len(df.index)):
        newfeel = is_new(row["feel"], row["old_feel"])
        newrelh = is_new(row["relh"], row["old_relh"])
        if not newfeel and not newrelh:
            skips += 1
            continue
        cursor.execute(
            f"UPDATE t{sts.year} SET feel = %s, relh = %s "
            "WHERE station = %s and valid = %s",
            (
                bnds_check(row["feel"], -80, 150),
                bnds_check(row["relh"], 0, 100),
                row["station"],
                row["valid"],
            ),
        )
        count += 1
        if count % 1000 == 0:
            cursor.close()
            pgconn.commit()
            cursor = pgconn.cursor()
    cursor.close()
    pgconn.commit()
    print(
        f"{sts:%Y%m%d} edit:{count} skip:{skips} rows finished in "
        f"{(utc() - start_time).total_seconds():.4f}s"
    )


if __name__ == "__main__":
    main()
