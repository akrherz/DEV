import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
font0 = FontProperties()
font0.set_weight('bold')

df = pd.read_excel("/tmp/ames.xlsx")
print df

(fig, ax) = plt.subplots(1, 1)

for _, row in df.iterrows():
    c = 'r' if row['Year'] in [2011, 2012, 2013] else 'k'
    c = 'g' if row['Year'] in [1980, 1992, 1993] else c
    ax.text(row['t'], row['p'], ("%i" % (row['Year'],))[-2:], color=c,
            ha='center')

ax.set_xlim(df['t'].min() - 0.3, df['t'].max() + 0.3)
ax.set_ylim(df['p'].min() - 10, df['p'].max() + 10)
ax.set_xlabel("Average Temperature ($^\circ$C)")
ax.set_ylabel("Cumulative Precipitation (cm)")

ax.text(0.15, 0.95, "Cool & Wet", ha='center', transform=ax.transAxes,
        fontproperties=font0)
ax.text(0.85, 0.95, "Warm & Wet", ha='center', transform=ax.transAxes,
        fontproperties=font0)
ax.text(0.85, 0.05, "Warm & Dry", ha='center', transform=ax.transAxes,
        fontproperties=font0)
ax.text(0.15, 0.05, "Cool & Dry", ha='center', transform=ax.transAxes,
        fontproperties=font0)
ax.axhline(df['p'].mean())
ax.axvline(df['t'].mean())

fig.savefig('test.png')
