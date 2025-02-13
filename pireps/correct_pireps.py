"""Fix damage from akrherz/pyIEM#442"""

from datetime import timedelta

import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn, sql_helper
from pyiem.nws.products.pirep import Pirep
from pyiem.util import logger, utc
from pywwa.workflows.pirep import LOCS, load_locs

LOG = logger()


def do(conn, dt):
    """do a date."""
    sts = utc(dt.year, dt.month, dt.day)
    table = f"pireps_{dt.year}"
    res = conn.execute(
        sql_helper(
            """
    SELECT ctid, st_x(geom::geometry), st_y(geom::geometry), report, valid
    from {table} WHERE valid >= :sts and valid < :ets and report ~* 'FLM'
        """,
            table=table,
        ),
        {"sts": sts, "ets": sts + timedelta(days=1)},
    )
    print(f"dt: {dt} found: {res.rowcount}")
    updates = 0
    for row in res.fetchall():
        fake = f"000 \r\r\nSAUS99 KDMX 241200\r\r\n{row[3]}=\r\r\n"
        p = Pirep(fake, nwsli_provider=LOCS)
        if not p.reports:
            print(fake)
            continue
        newlon = p.reports[0].longitude
        newlat = p.reports[0].latitude
        if newlon is None:
            print(fake)
            continue
        dist = ((newlon - row[1]) ** 2 + (newlat - row[2]) ** 2) ** 0.5
        if dist < 0.0001:
            continue
        print(f"dist: {dist} {row[1]} {row[2]} -> {newlon} {newlat}")
        artcc = """
    (select ident from airspaces where st_dwithin(geom,
        ST_Point(:lon, :lat, 4326), 0) and type_code = 'ARTCC' LIMIT 1)
    """
        conn.execute(
            sql_helper(
                """
    UPDATE {table} SET geom = ST_POINT(:lon, :lat, 4326), artcc = {artcc}
    WHERE valid = :valid and ctid = :ctid""",
                table=table,
                artcc=artcc,
            ),
            {"lon": newlon, "lat": newlat, "valid": row[4], "ctid": row[0]},
        )
        updates += 1


def main():
    """GO Main Go."""
    conn, cursor = get_dbconnc("postgis")
    load_locs(cursor)
    conn.close()
    with get_sqlalchemy_conn("postgis") as conn:
        for date in pd.date_range("2024/01/01", "2024/12/31"):
            do(conn, date)
            conn.commit()


if __name__ == "__main__":
    main()
