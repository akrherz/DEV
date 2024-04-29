"""Figure out who is doing what"""

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        """SELECT distinct phenomena, significance from warnings_2016
        ORDER by phenomena, significance
        """
    )
    print("PP.S CNTY ZONE")
    for row in cursor:
        phenomena = row[0]
        significance = row[1]
        df = read_sql(
            """SELECT wfo, substr(ugc, 3, 1) as z, count(*) from
        warnings_2016 where phenomena = %s and significance = %s
        GROUP by wfo, z ORDER by wfo""",
            pgconn,
            params=(phenomena, significance),
        )
        df1 = df[df["z"] == "C"]
        df2 = df[df["z"] == "Z"]
        (
            print(
                "%s.%s %4i %4i"
                % (phenomena, significance, len(df1.index), len(df2.index))
            ),
        )
        if df2.empty or df1.empty:
            continue
        if len(df2.index) < len(df1.index):
            print(" wfos using zones: %s" % (",".join(df2["wfo"].values),))
        if len(df2.index) > len(df1.index):
            print(" wfos using counties: %s" % (",".join(df1["wfo"].values),))

        g = df.groupby("wfo").count()
        g.sort_values("count")
        print(g)


if __name__ == "__main__":
    main()
