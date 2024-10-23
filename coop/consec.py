"""consec days"""

from datetime import timedelta

import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from tqdm import tqdm


def main():
    """Go Main Go"""
    with get_sqlalchemy_conn("coop") as conn:
        threaded = pd.read_sql(
            "select id from stations where "
            "network ~* 'CLIMATE' and substr(id, 3, 1) = 'T'",
            conn,
        )
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    maxduration = timedelta(days=1)
    for sid in tqdm(threaded["id"]):
        if sid == "AZTPHX":
            continue
        cursor.execute(
            """
        select sday, day, high, temp_estimated from
        alldata where station = %s and high is not null
        ORDER by day ASC
        """,
            (sid,),
        )
        por = None
        records = {}
        for dt in pd.date_range("2000/01/01", "2000/12/31"):
            records[f"{dt:%m%d}"] = -99
        running = 0
        for row in cursor:
            if por is None:
                por = row[1]
            if row[2] >= records[row[0]]:
                if not row[3]:
                    running += 1
                else:
                    running = 0
                records[row[0]] = row[2]
                if running >= 21:
                    duration = row[1] - por
                    if duration > maxduration:
                        maxduration = duration
                        print(f"{sid} {por} {row[1]} {duration}")
            else:
                running = 0


if __name__ == "__main__":
    main()
