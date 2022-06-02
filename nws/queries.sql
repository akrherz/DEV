-- Number of CON WSW statements made
with data as (
    select extract(year from issue) as year,
    array_length(string_to_array(svs, '__'), 1) - 2 as updates,
    eventid, phenomena, significance, status,
    wfo from warnings WHERE phenomena = 'WS' and significance = 'W'),
agg as (
    select year, max(case when status = 'NEW' then 0 when
    status in ('EXP', 'CAN', 'UPG') then updates - 1 else updates end)
    as logic, eventid, phenomena, significance, wfo from data
    GROUP by eventid, phenomena, significance, wfo, year),
agg2 as (
    select year, eventid, avg(logic) as cnt, phenomena, significance, wfo
    from agg GROUP by eventid, phenomena, significance, wfo, year)

select wfo, avg(cnt) from agg2 GROUP by wfo ORDER by wfo;

-- precentage of SVRs with tor possible, 2015 for nationwide impl
with data as (
    select wfo, eventid, extract(year from polygon_begin) as year,
    max(case when tornadotag = 'POSSIBLE' then 1 else 0 end) as hit
    from sbw where phenomena = 'SV' and polygon_begin > '2015-01-01'
    and status = 'NEW' group by wfo, eventid, year )
    select wfo, sum(hit) , count(*), sum(hit) / count(*)::float * 100.
    from data GROUP by wfo ORDER by wfo asc;
