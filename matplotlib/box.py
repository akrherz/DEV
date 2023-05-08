import calendar

import seaborn as sns

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn

pgconn = get_dbconn("afos")
df = read_sql(
    """
    select extract(month from entered)::int as month, len from bah""",
    pgconn,
)
gdf = df.groupby("month").mean()
print(gdf)
ax = sns.violinplot(x=df["month"], y=df["len"])
ax.set_ylim(0, 2000)
ax.set_title("NWS Average AFD Word Count by Month (2010-2020)")
xticklabels = []
for i in range(1, 13):
    xticklabels.append("%s\n%.0f" % (calendar.month_abbr[i], gdf.at[i, "len"]))
ax.set_xticklabels(xticklabels)
ax.set_xlabel("")
ax.grid(True)
ax.set_ylabel("Word Count per AFD")

plt.gcf().savefig("test.png")
