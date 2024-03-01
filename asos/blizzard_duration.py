"""Compute Longest Blizzard Criterion."""

from datetime import timedelta

import pandas as pd
from pyiem.util import get_dbconn, get_sqlalchemy_conn


def main():
    """Go"""
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            "SELECT id, st_x(geom) as lon, st_y(geom) as lat "
            "from stations where country = 'US' and "
            "network ~* 'ASOS' order by id asc",
            conn,
            index_col="id",
        )
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    for sid in [
        "BUF",
    ]:  # df.index.values:
        cursor.execute(
            """
        select valid, sknt * 1.15 as wind, vsby from alldata where
        station = %s and vsby <= 5 and sknt > 20
        and report_type in (3, 4) ORDER by valid asc
        """,
            (sid,),
        )
        now = None
        begin = None
        maxdelta = timedelta(minutes=0)
        for row in cursor:
            if now is None:
                now = row[0]
            if row[1] >= 34.5 and row[2] <= 0.25:
                if begin is None:
                    begin = row[0]
            else:
                if begin is not None:
                    delta = row[0] - begin
                    if delta > maxdelta:
                        print(sid, row[0], delta)
                        maxdelta = delta
                begin = None
        df.at[sid, "period"] = maxdelta


if __name__ == "__main__":
    main()
