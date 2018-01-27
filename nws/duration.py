import numpy as np
import matplotlib.pyplot as plt
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

pgconn = get_dbconn('postgis')

df = read_sql("""
    select extract(year from issue) as yr, phenomena,
    avg(init_expire - issue) as duration
    from warnings where phenomena in ('TO', 'SV') and significance = 'W'
    and issue < init_expire and issue < '2017-01-01'
    GROUP by yr, phenomena ORDER by yr ASC
    """, pgconn, index_col='yr')
df['minutes'] = df['duration'] / np.timedelta64(60, 's')

(fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
df2 = df[df['phenomena'] == 'TO']
ax.bar(df2.index.values - 0.2, df2['minutes'].values, color='r', lw=2,
       label='Tornado', align='center', width=0.4)
df2 = df[df['phenomena'] == 'SV']
ax.bar(df2.index.values + 0.2, df2['minutes'].values, color='b', lw=2,
       label='Severe TStorm', align='center', width=0.4)

ax.set_yticks(np.arange(0, 60 + 1, 5))
ax.set_ylabel("Minutes")
ax.legend(ncol=2)
ax.set_xlim(1985.5, 2016.5)
ax.set_title("1986-2016 NWS Initial Average Warning Duration")
ax.set_xlabel("based on unofficial archives maintained by the IEM, @akrherz")
ax.grid(True)

fig.savefig('test.png')
