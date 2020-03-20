"""Compare NWSLIs"""

import pandas as pd
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    dbconn = get_dbconn("mesosite")
    cursor = dbconn.cursor()
    df = pd.read_csv("/home/akrherz/Downloads/DVN_Coop.csv")
    for _i, row in df.iterrows():
        cursor.execute(
            """
        select network from stations where id = %s
        """,
            (row["SID"],),
        )
        if cursor.rowcount != 1:
            print("%s %s" % (row["SID"], cursor.rowcount))


if __name__ == "__main__":
    main()
