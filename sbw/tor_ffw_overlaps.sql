with tor as (
    select vtec_year as year, eventid, geom, issue, expire from sbw
    where wfo = 'DMX' and phenomena = 'TO' and significance = 'W'
    and status = 'NEW'),

ffw as (
    select vtec_year as year, eventid, geom, issue, expire from sbw
    where wfo = 'DMX' and phenomena = 'FF' and significance = 'W'
    and status = 'NEW')

select t.year, t.eventid, f.eventid, t.issue, f.issue, t.expire, f.expire
from tor t, ffw f WHERE ST_Intersects(t.geom, f.geom)
and f.issue < t.expire and t.issue < f.expire ORDER by t.issue DESC;
