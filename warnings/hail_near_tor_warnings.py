"""Requested dataset of hail near TORs."""

import geopandas as gpd
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go do things."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            """
            -- List of TOR LSRs that had a warning polygon with it.
            with tors as (
                select l.geom, l.valid, w.wfo, w.eventid,
                extract(year from l.valid) as year, w.issue, w.expire
                from sbw w, lsrs l
                where w.phenomena = 'TO' and
                w.significance = 'W' and w.status = 'NEW' and
                ST_Intersects(w.geom, l.geom) and w.wfo = l.wfo
                and w.issue <= l.valid and w.expire >= l.valid
                and l.typetext = 'TORNADO'
            )
            -- Look for hail reports within 100km of the TOR report
            select t.wfo, t.eventid, t.year, st_x(t.geom) as torlon,
            st_y(t.geom) as torlat, l.magnitude, t.geom,
            st_x(l.geom) as haillon, st_y(l.geom) as haillat,
            l.valid at time zone 'UTC' as hailvalid,
            t.issue at time zone 'UTC' as torissue,
            t.expire at time zone 'UTC' as torexpire,
            ST_Distance(t.geom::geography, l.geom::geography) as distance_m
            from tors t, lsrs l WHERE
            ST_DWithin(l.geom::geography, t.geom::geography, 100000, 't')
            and l.valid >= t.issue and l.valid <= t.expire and
            l.typetext= 'HAIL'
            """,
            conn,
            geom_col="geom",
        )
    df.drop("geom", axis=1).to_csv("/tmp/hail_near_tor.csv", index=False)


if __name__ == "__main__":
    main()
