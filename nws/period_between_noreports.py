"""
with days as (select generate_series('2003-01-01'::date, '2016-08-24'::date, 
'1 day'::interval) as d, 0 as cnt), obs as (select date(valid - '12 hours'::interval)
 as d, count(*) as cnt from lsrs WHERE type in ('H', 'G', 'D', 'T') GROUP by d), 
 agg1 as (select d.d, d.cnt, coalesce(o.cnt, 0) as cnt2 from days d LEFT JOIN obs o
  ON (d.d = o.d)) select extract(year from d) as yr, max(case when 
  extract(month from d) < 7 then d else null end), 
  min(case when extract(month from d) >= 7 then d else null end) from agg1 
  where cnt2 = 0 GROUP by yr ORDER by yr;

"""
import datetime
import calendar
import matplotlib.pyplot as plt
data = """  2003 | 2003-05-21 00:00:00+00 | 2003-09-19 00:00:00+00
 2004 | 2004-05-03 00:00:00+00 | 2004-09-02 00:00:00+00
 2005 | 2005-04-14 00:00:00+00 | 2005-10-08 00:00:00+00
 2006 | 2006-03-22 00:00:00+00 | 2006-10-17 00:00:00+00
 2007 | 2007-04-08 00:00:00+00 | 2007-10-03 00:00:00+00
 2008 | 2008-04-13 00:00:00+00 | 2008-09-15 00:00:00+00
 2009 | 2009-04-03 00:00:00+00 | 2009-10-21 00:00:00+00
 2010 | 2010-04-09 00:00:00+00 | 2010-10-16 00:00:00+00
 2011 | 2011-03-12 00:00:00+00 | 2011-10-20 00:00:00+00
 2012 | 2012-02-16 00:00:00+00 | 2012-09-15 00:00:00+00
 2013 | 2013-03-26 00:00:00+00 | 2013-09-26 00:00:00+00
 2014 | 2014-05-02 00:00:00+00 | 2014-09-28 00:00:00+00
 2015 | 2015-04-29 00:00:00+00 | 2015-09-21 00:00:00+00
 2016 | 2016-04-03 00:00:00+00 | 2016-08-23 00:00:00+00"""


y = []
x = []
d = []
stss = []
etss = []
for line in data.split("\n"):
    tokens = line.strip().split("|")
    print tokens
    sts = datetime.datetime.strptime(tokens[1].strip(), '%Y-%m-%d %H:%M:%S+00')
    ets = datetime.datetime.strptime(tokens[2].strip(), '%Y-%m-%d %H:%M:%S+00')
    year = int(tokens[0])
    days = (ets - sts).days
    stss.append(sts)
    etss.append(ets)
    y.append(year)
    x.append(int(sts.strftime("%j")))
    d.append(days)

(fig, ax) = plt.subplots(1, 1)
ax.barh(y, d, left=x, align='center')
for year, xdate, days, sts, ets in zip(y, x, d, stss, etss):
    ax.text(xdate - 1, year, "%s" % (sts.strftime("%-d %b"),), ha='right',
            va='center', bbox=dict(color='white'))
    ax.text(xdate + days + 1, year, "%s -> %.0fd" % (ets.strftime("%-d %b"),
                                                     days), va='center',
            bbox=dict(color='white'))
ax.grid(True)
ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335,
               365))
ax.set_xticklabels(calendar.month_abbr[1:])
ax.set_xlim(0, 380)
ax.set_ylim(2002.5, 2016.5)
ax.set_title(("Period Between 'Day' without Severe T'Storm nor Tornado Report\n"
              "Day representing a 12 UTC to 12 UTC Period"))
fig.text(0.02, 0.02, "Generated 22 Aug 2016, @akrherz")


fig.savefig('test.png')
