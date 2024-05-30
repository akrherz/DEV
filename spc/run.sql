-- Get the outlook valid for Tornado Watches
with watches as (
    select w.ugc, u.geom, w.issue, w.expire from warnings_2017 w JOIN ugcs u
    on (w.gid = u.gid) WHERE  w.phenomena = 'TO'
    and w.significance = 'A'),

agg as (
    select w.ugc, o.threshold, o.valid as outlook_valid,
    o.issue as outlook_issue, o.expire as outlook_expire,
    w.issue as watch_issue
    from watches w LEFT JOIN spc_outlooks o ON (ST_Intersects(w.geom, o.geom)
        and w.issue > o.valid and w.issue < o.expire)
    WHERE o.day = 1 and o.outlook_type = 'C' and o.category = 'CATEGORICAL'),

agg2 as (
    SELECT a.*, t.priority,
    rank() OVER (PARTITION by ugc, watch_issue, outlook_expire
        ORDER by outlook_valid DESC, t.priority DESC)
    from agg a JOIN spc_outlook_thresholds t
    on (a.threshold = t.threshold))

SELECT threshold, count(*) from agg2 WHERE rank = 1 GROUP by threshold;


with mods as (
    select expire, geom, threshold from spc_outlooks where
    outlook_type = 'C' and day = 1 and threshold = 'MDT'
    and extract(hour from valid at time zone 'UTC') in (12, 13)
    and category = 'CATEGORICAL' and st_isvalid(geom)),
    
slis as (
    select expire, geom, threshold from spc_outlooks where
    outlook_type = 'C' and day = 1 and threshold = 'SLGT'
    and extract(hour from valid at time zone 'UTC') in (12, 13)
    and category = 'CATEGORICAL' and st_isvalid(geom)),

agg as (
    SELECT s.expire, st_area(m.geom) / st_area(s.geom) * 100. as ratio,
    st_area(s.geom) as slis_geom, st_area(m.geom) as mdt_geom
    from slis s JOIN mods m on (s.expire = m.expire))

SELECT extract(year from expire) as yr, avg(ratio), avg(slis_geom), avg(mdt_geom) from agg
GROUP by yr ORDER by yr;
    