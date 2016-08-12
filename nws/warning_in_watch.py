"""
with warns as (select ugc, issue, expire from warnings where phenomena = 'SV' and significance ='W' and issue > '2005-10-01'), watch as (select ugc, issue, expire from warnings where phenomena in ('SV', 'TO') and significance = 'A'), agg as ( SELECT w.ugc, w.issue as w_issue, w.expire, a.ugc as a_ugc, a.issue, a.expire from warns w LEFT JOIN watch a on (w.ugc = a.ugc and w.issue < a.expire and w.expire > a.issue)), agg2 as (SELECT extract(week from w_issue) as week, count(*), sum(case when a_ugc is not null then 1 else 0 end) from agg GROUP by week)  select week, sum / count::float * 100 from agg2 ORDER by week;


"""

import matplotlib.pyplot as plt
import calendar

# TOR
data = """    1 | 83.9884153909805
    2 | 90.9427966101695
    3 | 89.5486111111111
    4 | 91.4988650508896
    5 |  86.516322346633
    6 | 80.6090739589807
    7 | 70.3950499762018
    8 | 63.6651870640457
    9 |  71.568345323741
   10 | 79.3103448275862
   11 |   86.76293622142
   12 | 84.8294786358291"""

# SVR
data = """    1 | 74.2490340271719
    2 | 76.1897904816761
    3 | 69.8463416385438
    4 |  74.163173561752
    5 | 63.3073466219098
    6 |  57.577623971237
    7 | 46.3328950612211
    8 | 40.5505631543543
    9 |  45.826030808966
   10 | 62.7282491944146
   11 | 71.5146645239052
   12 | 71.7070142768467"""

x = range(1, 13)
y = []
for line in data.split("\n"):
    tokens = line.strip().split(" | ")
    y.append(float(tokens[1]))

(fig, ax) = plt.subplots(1, 1)

ax.bar(x, y, align='center', fc='yellow')
for x0, y0 in zip(x, y):
    ax.text(x0, y0 + 3, "%.0f%%" % (y0,), ha='center')
ax.set_xlim(0.5, 12.5)
ax.grid(True)
ax.set_xticks(x)
ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
ax.set_xticklabels(calendar.month_abbr[1:])
ax.set_title(("Percentage of County Based Severe T'Storm Warnings within\n"
              "a SPC Severe T'storm or Tornado Watch (Oct 2005-Aug 2016)"))

fig.text(0.02, 0.02, "@akrherz Iowa Environmental Mesonet 11 August 2016",
         fontsize=10)

fig.savefig('test.png')
