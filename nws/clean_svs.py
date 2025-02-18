"""Our SVS dataset sometimes 'corrupts' with duplicated ETNs within a year"""

import datetime
import sys

import psycopg2
from pyiem.nws.products import parser


def main():
    POSTGIS = psycopg2.connect(database="postgis")
    cursor = POSTGIS.cursor()
    cursor2 = POSTGIS.cursor()

    table = "warnings_%s" % (sys.argv[1],)

    cursor.execute(
        f"""
    SELECT oid, svs from {table} where
    (expire - issue) > '3 hours'::interval and phenomena in ('SV', 'TO')
    and significance = 'W'
    """
    )
    for row in cursor:
        oid = row[0]
        svs = row[1]
        times = []
        svss = []
        for svs in row[1].split("__"):
            if svs.strip() == "":
                continue
            try:
                p = parser(svs)
            except Exception:
                continue
            times.append(p.valid)
            svss.append(svs)
        if len(times) < 2:
            continue
        delta = times[-1] - times[0]
        for i, _time in enumerate(times):
            if i == 0:
                continue
            delta = times[i] - times[i - 1]
            if delta < datetime.timedelta(days=1):
                continue
            print(
                "Discontinuity %s %s %s %s" % (oid, i, times[i - 1], times[i])
            )
            newsvs = "__".join(svss[:i]) + "__"
            cursor2.execute(
                """UPDATE """
                + table
                + """ SET svs = %s WHERE oid = %s
            """,
                (newsvs, oid),
            )

    cursor2.close()
    POSTGIS.commit()


if __name__ == "__main__":
    main()
