"""Remove any duplicated rows with differenting temperatures

A stop gap hack to remove some bad data from the database.  Sadly, gonna be
tough to resolve how these obs appeared in the database to begin with :(
"""

import pandas as pd
from pyiem.database import get_dbconn
from tqdm import tqdm


def do_year(year):
    """Process this year"""
    pgconn = get_dbconn("asos")
    table = f"t{year}"
    stations = pd.read_sql(
        f"SELECT distinct station from {table} ORDER by station",
        pgconn,
    )
    progress = tqdm(stations["station"].values)
    for station in progress:
        progress.set_description(f"{station}")
        while True:
            cursor = pgconn.cursor()
            cursor.execute(
                f"""with obs as (
                    select valid, count(*), max(ctid) from {table}
                    where station = %s and report_type in (3, 4) GROUP by valid
                    ORDER by count DESC)
                delete from {table} t USING obs o where
                t.ctid = o.max and t.station = %s and o.count > 1
                """,
                (station, station),
            )
            if cursor.rowcount > 0:
                print(f"{station} deleted {cursor.rowcount} rows")
                pgconn.commit()
                cursor.close()
                continue
            cursor.close()
            break


def main():
    """Go Main"""
    for year in range(2011, 2012):
        do_year(year)


if __name__ == "__main__":
    main()
