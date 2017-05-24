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
    