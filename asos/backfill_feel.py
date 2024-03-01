"""Fill in the hole of feel column."""

import datetime
import sys

import numpy as np

import metpy.calc as mcalc
import pandas as pd
from metpy.units import units
from pyiem.util import get_dbconn, get_sqlalchemy_conn, utc


def not_nan(val):
    """Make sure this is not NaN."""
    return None if pd.isnull(val) else float(val)


def main(argv):
    """Go Main Go."""
    start_time = datetime.datetime.now()
    sts = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    ets = sts + datetime.timedelta(hours=24)
    pgconn = get_dbconn("asos")
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            f"""
        SELECT station, valid, tmpf, dwpf, sknt, relh, feel from t{sts.year}
        WHERE valid >= %s and valid < %s and tmpf >= dwpf
        and (feel is null or relh is null)
        """,
            conn,
            params=(sts, ets),
            index_col=None,
        )
    print(
        f"{sts:%Y%m%d} query of {len(df.index)} rows finished in "
        f"{(datetime.datetime.now() - start_time).total_seconds():.4f}s"
    )
    start_time = datetime.datetime.now()
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
    for _, row in df[df["dirty"]].iterrows():
        newfeel = not_nan(row["feel"])
        newrelh = not_nan(row["relh"])
        if newfeel is None and newrelh is None:
            skips += 1
            continue
        cursor.execute(
            f"UPDATE t{sts.year} SET feel = %s, relh = %s "
            "WHERE station = %s and valid = %s",
            (
                newfeel,
                newrelh,
                row["station"],
                row["valid"],
            ),
        )
        if count > 1000 and count % 1000 == 0:
            cursor.close()
            pgconn.commit()
            cursor = pgconn.cursor()
        count += 1
    cursor.close()
    pgconn.commit()
    print(
        f"{sts:%Y%m%d} edit:{count} skip:{skips} rows finished in "
        f"{(datetime.datetime.now() - start_time).total_seconds():.4f}s"
    )


if __name__ == "__main__":
    main(sys.argv)
