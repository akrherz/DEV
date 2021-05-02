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
                SELECT valid, tmpf::int as tmpf, dwpf::int as dwpf
                from t2021 where station = %s and
                valid > '2021-05-01 00:50' and valid < '2021-05-01 23:00'
                and tmpf is not null and dwpf is not null
                ORDER by tmpf DESC LIMIT 1
            )
            select a.valid, a.tmpf, a.dwpf,
            t.valid as t_valid, t.tmpf as t_tmpf, t.dwpf as t_dwpf
            from alldata a, today t
            where station = %s and a.valid <= t.valid and
            a.tmpf::int >= t.tmpf and a.dwpf::int <= t.dwpf ORDER by valid DESC
            """,
            (station, station),
        )
        row1 = cursor.fetchone()
        row2 = None
        hours = 0
        for row in cursor:
            if row[0].strftime("%Y%m%d") != "20210501":
                if row2 is None:
                    row2 = row
                hours += 1
        print(f"{station} {hours} {row1[1]} {row2}")


if __name__ == "__main__":
    main()
