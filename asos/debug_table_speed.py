"""Debug printout of partitioned table speed within ASOS database"""

from datetime import datetime

import click
from pyiem.database import get_dbconn


@click.command()
@click.option("--station", help="Station ID to query", required=True)
def main(station: str):
    """Go Main Go"""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    maxt = 0
    for yr in range(1928, datetime.now().year + 1):
        sts = datetime.now()
        cursor.execute(
            f"SELECT count(*) from t{yr} WHERE station = %s",
            (station,),
        )
        row = cursor.fetchone()
        ets = datetime.now()
        secs = (ets - sts).total_seconds()
        tt = " <-- " if secs > maxt else ""
        print(f"{yr} {row[0]:6.0f} {secs:8.4f}{tt}")
        maxt = max([secs, maxt])


if __name__ == "__main__":
    main()
