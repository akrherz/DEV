"""Dump a hurricane's worth of data."""
from pandas.io.sql import read_sql
import pandas as pd
from pyiem.util import get_dbconn


def main():
    """Go Main."""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        """
        select substr(w.ugc, 1, 2) as state, w.ugc, name, phenomena,
        significance, product_issue, issue, expire from warnings_2018 w
        JOIN ugcs u on (w.gid = u.gid) WHERE eventid = 1014
    """,
        pgconn,
        index_col=None,
    )
    writer = pd.ExcelWriter(
        "michael.xlsx", engine="xlsxwriter", options={"remove_timezone": True}
    )
    df.to_excel(writer, sheet_name="Events", index=False)
    writer.save()


if __name__ == "__main__":
    main()
