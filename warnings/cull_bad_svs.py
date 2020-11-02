"""see akrherz/iem#191

Dedup some duplicated FFWs in the warnings table."""
import sys

from pyiem.util import get_dbconn
from pyiem.nws.product import TextProduct
from pandas.io.sql import read_sql


def main(argv):
    """Go for this year."""
    year = int(argv[1])
    phenomena = argv[2]
    significance = argv[3]
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    # Candidates have 2003 in their SVS
    df = read_sql(
        f"SELECT ctid, svs, issue from warnings_{year} WHERE "
        "phenomena = %s and significance = %s "
        "and svs ~* ' 2003'",
        pgconn,
        index_col=None,
        params=(phenomena, significance),
    )
    print("%s entries for dedup found" % (len(df.index),))
    for _, row in df.iterrows():
        svses = row["svs"].split("__")
        keep = []
        for svs in svses:
            if svs.strip() == "":
                continue
            try:
                prod = TextProduct(svs)
            except Exception as exp:
                print(exp)
                continue
            print(prod.valid)
            if prod.valid.year != 2003:
                keep.append(prod.unixtext)
        cursor.execute(
            f"UPDATE warnings_{year} SET svs = %s where ctid = %s",
            ("__".join(keep), row["ctid"]),
        )

    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
