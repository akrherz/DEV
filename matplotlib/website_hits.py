import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_table("hits_by_second.txt", sep=",")
df.columns = ["ts", "hits"]
df["valid"] = pd.to_datetime(df["ts"], format="%Y%m%d%H%M%S")

(fig, ax) = plt.subplots(1, 1)

ax.bar(
    df["valid"].values, df["hits"].values, width=1 / 86400.0, ec="b", fc="b"
)
ax.grid(True)
ax.set_xlim(
    datetime.datetime(2016, 11, 2, 22, 15),
    datetime.datetime(2016, 11, 2, 23, 15),
)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I:%M"))
ax.set_xlabel("Evening of 2 Nov 2016, CDT")
ax.set_ylabel("Website Requests per Second")

ax.annotate(
    "10:23 PM\nRain Starts",
    xy=(datetime.datetime(2016, 11, 2, 22, 23), 20000.0),
    xycoords="data",
    xytext=(-50, 30),
    textcoords="offset points",
    bbox=dict(boxstyle="round", fc="0.8"),
    arrowprops=dict(
        arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=1"
    ),
)
ax.annotate(
    "10:54 PM\nTarp is Rolled Out!",
    xy=(datetime.datetime(2016, 11, 2, 22, 54), 20000.0),
    xycoords="data",
    xytext=(-50, 30),
    textcoords="offset points",
    bbox=dict(boxstyle="round", fc="0.8"),
    arrowprops=dict(
        arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=1"
    ),
)

ax.set_title("IEM WebFarm Traffic During 2016 Cubs+Indians Game 7")

fig.savefig("test.png")
