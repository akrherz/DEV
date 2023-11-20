import matplotlib.pyplot as plt
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

pgconn = get_dbconn("postgis")
df = read_sql(
    """
with watches as (
  SELECT ugc, eventid, extract(year from issue) as yr,
  issue, expire from warnings WHERE
  phenomena = 'SV' and significance = 'A' and issue > '2005-10-01'),

warnings as (
  SELECT ugc, extract(year from issue) as yr,
  eventid, issue, expire from warnings where
  phenomena = 'SV' and significance = 'W' and issue > '2005-10-01'),
verif as (
    SELECT distinct w.ugc, w.yr, a.eventid from warnings w JOIN watches a
    on (w.ugc = a.ugc and w.issue >= a.issue and w.issue < a.expire
    and w.yr = a.yr)
),
watch_combo as (
  SELECT eventid, yr, count(*) from watches GROUP by eventid, yr
  ),
warn_combo as (
  SELECT eventid, yr, count(*) from verif GROUP by eventid, yr
)

SELECT a.eventid, a.yr, a.count as issue_zones, w.count as warning_zones
from watch_combo a LEFT JOIN warn_combo w on (a.yr = w.yr
and a.eventid = w.eventid)

""",
    pgconn,
    index_col=None,
)
df.fillna(0, inplace=True)
df["percent"] = df["warning_zones"] / df["issue_zones"] * 100.0
print(df)

total = float(len(df.index))
xs = [
    "0",
    "1-10",
    "11-20",
    "21-30",
    "31-40",
    "41-50",
    "51-60",
    "61-70",
    "71-80",
    "81-90",
    "91-100",
]
ys = [len(df[df["percent"] == 0].index) / total * 100.0]
for x in xs[1:]:
    x1, x2 = [float(i) for i in x.split("-")]
    ys.append(
        len(df[(df["percent"] >= x1) & (df["percent"] < (x2 + 1))].index)
        / total
        * 100.0
    )

(fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

ax.bar(range(len(xs)), ys, align="center", color="tan")
for i, y in enumerate(ys):
    ax.text(i, y + 0.25, "%.1f%%" % (y,), ha="center")
ax.set_xticks(range(len(xs)))
ax.set_xticklabels(xs)
ax.set_title(
    "1 Oct 2005 - 28 Mar 2017 "
    "Svr Tstorm Watch into Svr Tstorm Warning Coverage\n"
    "Frequency of watches with percentage of counties/parishes under...\n"
    "Svr Tstorm Watch eventually receiving a Svr Tstorm Warning"
)

ax.grid(True)
fig.text(0.01, 0.01, "@akrherz, 29 Mar 2017")
ax.set_xlabel(
    (
        "Percentage of Counties/Parishes in Svr Tstorm Watch "
        "getting at least 1 Svr Tstorm Warning"
    )
)
ax.set_ylabel("Watch Frequency [%]")

fig.savefig("test.png")
