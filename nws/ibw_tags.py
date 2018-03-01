"""A plot of IBW tags"""
import numpy as np
import matplotlib.pyplot as plt
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn
pgconn = get_dbconn('postgis')

df = read_sql("""
    SELECT windtag, hailtag, issue from sbw WHERE (windtag > 0 or hailtag > 0)
    and status = 'NEW'
    and phenomena = 'SV'
    """, pgconn, index_col=None)
# bogus column so that groupby works
df['cnt'] = 1
minvalid = df['issue'].min()
maxvalid = df['issue'].max()
del df['issue']
df = df.fillna(0)
total = len(df.index) * 1.
uniquehail = df['hailtag'].unique().tolist()
uniquehail.sort()
uniquehail = uniquehail[::-1]
uniquewind = df['windtag'].astype(int).unique().tolist()
uniquewind.sort()

df = df.groupby(by=['hailtag', 'windtag']).count()

(fig, ax) = plt.subplots(figsize=(8, 6))
data = np.zeros((len(uniquewind), len(uniquehail)))
for (hailtag, windtag), row in df.iterrows():
    y = uniquehail.index(hailtag)
    x = uniquewind.index(windtag)
    val = row['cnt'] / total * 100.
    ax.text(x, y, "%.2f" % (val, ), ha='center',
            color='r' if val >= 10 else 'k',
            va='center', bbox=dict(color='white'))

for hailtag, row in df.reset_index().groupby('hailtag').sum().iterrows():
    y = uniquehail.index(hailtag)
    x = len(uniquewind)
    val = row['cnt'] / total * 100.
    ax.text(x, y, "%.2f" % (val, ), ha='center',
            color='r' if val >= 10 else 'k',
            va='center', bbox=dict(color='white'))

for windtag, row in df.reset_index().groupby('windtag').sum().iterrows():
    y = -1
    x = uniquewind.index(windtag)
    val = row['cnt'] / total * 100.
    ax.text(x, y, "%.2f" % (val, ), ha='center',
            color='r' if val >= 10 else 'k',
            va='center', bbox=dict(color='white'))

ax.set_xticks(range(len(uniquewind) + 1))
ax.set_yticks(range(-1, len(uniquehail) + 1))
ax.set_xlim(-0.5, len(uniquewind) + 0.5)
ax.set_ylim(-1.5, len(uniquehail) - 0.5)
ax.set_xticklabels(uniquewind + ['Total'])
ax.set_yticklabels(['Total'] + uniquehail)
ax.xaxis.tick_top()
ax.set_xlabel("Wind Speed [mph]")
ax.set_ylabel("Hail Size [inch]")
ax.xaxis.set_label_position('top')
plt.tick_params(top='off', bottom='off', left='off', right='off')
for spine in plt.gca().spines.values():
    spine.set_visible(False)
fig.suptitle(("Frequency [%%] of NWS Wind/Hail Tags for "
              "Severe Thunderstorm Warning Issuance\n"
              "%s through %s, %.0f warnings\n"
              "All WFOs considered, * not all have same implementation dates!\n"
              "Values larger than 10%% in red"
              ) % (minvalid.strftime("%d %b %Y"),
                   maxvalid.strftime("%d %b %Y"), total))
ax.set_position([0.15, 0.02, 0.8, 0.75])

fig.savefig('test.png')
