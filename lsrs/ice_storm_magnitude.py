"""LSR Magnitude is empty for ice-storm."""

from pandas import read_sql
from pyiem.nws.lsr import _icestorm_remark
from pyiem.util import get_dbconn, get_dbconnstr


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    df = read_sql(
        "SELECT remark, ctid, tableoid::regclass as tablename from lsrs "
        "where magnitude is null and typetext = 'ICE STORM' ",
        get_dbconnstr("postgis"),
    )
    df["val"] = 0
    for idx, row in df.iterrows():
        val = _icestorm_remark(row["remark"])
        if val is None and row["remark"].find("INCH") > -1:
            print(f"------> {row['remark']}")
        if val is None:
            continue
        df.at[idx, "val"] = val
        cursor.execute(
            f"UPDATE {row['tablename']} SET magnitude = %s, unit = 'INCH', "
            "qualifier = 'U' WHERE ctid = %s RETURNING typetext",
            (val, row["ctid"]),
        )
        assert cursor.fetchone()[0] == "ICE STORM"

    df = df.sort_values("val", ascending=True, na_position="last")
    for idx, row in df.head(10).iterrows():
        print(f"{idx} {row['val']} {row['remark']}")

    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
