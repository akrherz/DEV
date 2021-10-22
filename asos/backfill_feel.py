"""Fill in the hole of feel column."""
import sys
import math
import datetime

from pyiem.util import get_dbconn, utc
from metpy.units import units
import metpy.calc as mcalc
from pandas.io.sql import read_sql


def not_nan(val):
    """Make sure this is not NaN."""
    val = float(val)
    return val if not math.isnan(val) else None


def main(argv):
    """Go Main Go."""
    start_time = datetime.datetime.now()
    sts = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    ets = sts + datetime.timedelta(hours=24)
    pgconn = get_dbconn("asos")
    df = read_sql(
        f"""
    SELECT station, valid, tmpf, dwpf, sknt, relh from t{sts.year}
    WHERE valid >= %s and valid < %s and tmpf >= dwpf and feel is null
    """,
        pgconn,
        params=(sts, ets),
        index_col=None,
    )
    print(
        f"{sts:%Y%m%d} query of {len(df.index)} rows finished in "
        f"{(datetime.datetime.now() - start_time).total_seconds():.4f}s"
    )
    start_time = datetime.datetime.now()
    # df["relh"] = (
    #    mcalc.relative_humidity_from_dewpoint(
    #        df["tmpf"].values * units.degF, df["dwpf"].values * units.degF
    #    )
    #    .to(units.percent)
    #    .magnitude
    # )
    df["feel"] = (
        mcalc.apparent_temperature(
            df["tmpf"].values * units.degF,
            df["relh"].values * units.percent,
            df["sknt"].values * units.knots,
            mask_undefined=False,
        )
        .to(units.degF)
        .magnitude
    )
    # df2 = df[(df["relh"] > 1) & (df["relh"] < 100.1)]
    cursor = pgconn.cursor()
    count = 0
    for _, row in df.iterrows():
        cursor.execute(
            f"UPDATE t{sts.year} SET feel = %s "
            "WHERE station = %s and valid = %s",
            (
                not_nan(row["feel"]),
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
        f"{sts:%Y%m%d} edit of {count} rows finished in "
        f"{(datetime.datetime.now() - start_time).total_seconds():.4f}s"
    )


if __name__ == "__main__":
    main(sys.argv)
