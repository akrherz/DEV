"""List out some records."""

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def main():
    """GO Main go."""
    nt = NetworkTable("IA_ASOS")
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    for station in nt.sts:
        if station in ["BRL"]:  # Offline
            continue
        cursor.execute(
            """
            WITH today as (
                SELECT max(tmpf)::int as tmpf from t2020 where station = %s and
                valid > '2020-07-19 04:50' and valid < '2020-07-19 05:00'
            )
            select valid, a.tmpf from alldata a, today t where station = %s and
            extract(hour from valid + '10 minutes'::interval) = 5 and
            a.tmpf::int >= t.tmpf ORDER by valid DESC
            """,
            (station, station),
        )
        row1 = cursor.fetchone()
        row2 = None
        if cursor.rowcount > 1:
            row2 = cursor.fetchone()
            while row2[0].strftime("%Y%m%d") == "20200719":
                row2 = cursor.fetchone()
        print(f"{station} {row1[1]} {row2}")


if __name__ == "__main__":
    main()
