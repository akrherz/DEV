"""Fill in the hole of feel column."""
import sys
import math
import datetime

from metpy.units import units
import metpy.calc as mcalc
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, utc


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
    table = "t%s" % (sts.year,)
    df = read_sql(
        """
    SELECT station, valid, tmpf, dwpf, sknt from """
        + table
        + """
    WHERE valid >= %s and valid < %s and tmpf >= dwpf
    and sknt is not null and feel is null
    """,
        pgconn,
        params=(sts, ets),
        index_col=None,
    )
    print(
        ("%s query of %s rows finished in %.4fs")
        % (
            sts.strftime("%Y%m%d"),
            len(df.index),
            (datetime.datetime.now() - start_time).total_seconds(),
        )
    )
    start_time = datetime.datetime.now()
    df["relh"] = (
        mcalc.relative_humidity_from_dewpoint(
            df["tmpf"].values * units.degF, df["dwpf"].values * units.degF
        )
        .to(units.percent)
        .magnitude
    )
    df["feel"] = (
        mcalc.apparent_temperature(
            df["tmpf"].values * units.degF,
            df["relh"].values * units.percent,
            df["sknt"].values * units.knots,
        )
        .to(units.degF)
        .magnitude
    )
    df2 = df[(df["relh"] > 1) & (df["relh"] < 100.1)]
    cursor = pgconn.cursor()
    count = 0
    for _, row in df2.iterrows():
        cursor.execute(
            """UPDATE """
            + table
            + """
        SET feel = %s, relh = %s WHERE station = %s and valid = %s
        """,
            (
                not_nan(row["feel"]),
                not_nan(row["relh"]),
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
        ("%s edit of %s rows finished in %.4fs")
        % (
            sts.strftime("%Y%m%d"),
            count,
            (datetime.datetime.now() - start_time).total_seconds(),
        )
    )


if __name__ == "__main__":
    main(sys.argv)
