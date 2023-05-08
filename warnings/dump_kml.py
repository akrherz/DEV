"""Dump TOR polys and SVR 70+"""

import fiona

import geopandas as gpd
from geopandas import read_postgis
from pyiem.util import get_dbconn

gpd.io.file.fiona.drvsupport.supported_drivers["LIBKML"] = "rw"
gpd.io.file.fiona.drvsupport.supported_drivers["libkml"] = "rw"


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    df = read_postgis(
        """
    with tors as (
        SELECT issue, expire, s.geom from sbw s, ugcs u WHERE s.wfo = 'DMX' and
        phenomena = 'TO' and status = 'NEW' and ST_Intersects(s.geom, u.geom)
        and u.ugc in ('IAC181', 'IAC153', 'IAC049')
    ), svrs as (
        SELECT issue, expire, s.geom, extract(year from issue) as year,
        eventid from sbw s, ugcs u WHERE s.wfo = 'DMX' and
        phenomena = 'SV' and status = 'NEW' and ST_Intersects(s.geom, u.geom)
        and u.ugc in ('IAC181', 'IAC153', 'IAC049')
    ), svrcand as (
        SELECT distinct extract(year from issue) as year, eventid from sbw
        WHERE wfo = 'DMX' and phenomena = 'SV' and windtag >= 70
    ), svrs2 as (
        select s.* from svrs s JOIN svrcand c on
        (s.year = c.year and s.eventid = c.eventid)
    ), agg as (
        SELECT *, 'TOR' as type from tors UNION
        select issue, expire, geom, 'SVR' as type from svrs2)

    select to_char(issue, 'YYYY-mm-dd HH24:MI') as issue,
    to_char(expire, 'YYYY-mm-dd HH24:MI') as expire, type, geom from agg
    """,
        pgconn,
        geom_col="geom",
    )
    with fiona.Env():
        df.to_file("wdsm.kml")


if __name__ == "__main__":
    main()
