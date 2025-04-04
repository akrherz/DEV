with data as (
    select valid, metar, substring(metar from ' (\d{2})/\d{2} ') as temp,
    substring(metar from ' \d{2}/(\d{2}) ') as dewp,
    substring(metar from ' T(\d{4})(\d{4})') AS first,
    substring(metar from ' T\d{4}(\d{4})') AS second from t2024
    where report_Type = 3 and metar ~* ' T' and length(station) = 3
    and valid > '2024-07-01'),

agg as (
    select valid, metar,
    abs(temp::int - round((first::float / 10.)::numeric, 0)) > 1 as cc, temp,
    first from data where temp is not null and first is not null)

select *, temp::int - round((first::float / 10.)::numeric, 0) from agg
where cc order by valid;
