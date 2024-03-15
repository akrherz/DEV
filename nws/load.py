"""Warning load by minute

Moved to https://mesonet.agron.iastate.edu/plotting/auto/?q=251
"""

import datetime
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_dbconn
from pyiem.nws.vtec import NWS_COLORS
from pyiem.plot import figure_axes

TZ = ZoneInfo("America/Chicago")
PGCONN = get_dbconn("postgis")


def getp(phenomena, sts, ets):
    """Do Query"""
    cursor = PGCONN.cursor()
    print(f"{sts} {ets}")
    cursor.execute(
        """
     WITH data as (
        select distinct wfo, eventid, phenomena,
        generate_series(issue, expire, '1 minute'::interval) as t
        from warnings where vtec_year = %s and issue > %s and
        issue < %s and phenomena = %s and significance = 'W'),
    agg as (
        SELECT t, count(*) from data GROUP by t
    ),
     ts as (
        select generate_series(%s, %s, '1 minute'::interval) as t
    )

     SELECT ts.t, agg.count from ts LEFT JOIN agg on (ts.t = agg.t)
     ORDER by ts.t ASC
    """,
        (sts.year, sts, ets, phenomena, sts, ets),
    )
    times = []
    counts = []
    for row in cursor:
        times.append(row[0])
        counts.append(row[1] if row[1] is not None else 0)

    return times, counts


def main(date):
    """Main"""
    sts = date - datetime.timedelta(hours=24)
    ets = date + datetime.timedelta(hours=24)
    to_t, to_c = getp("TO", sts, ets)
    _, sv_c = getp("SV", sts, ets)
    _, ff_c = getp("FF", sts, ets)
    df = pd.DataFrame(
        {"t": to_t, "to_c": to_c, "sv_c": sv_c, "ff_c": ff_c}
    ).set_index("t")
    df["b_c"] = df["to_c"] + df["ff_c"]
    df["a_c"] = df["to_c"] + df["sv_c"] + df["ff_c"]
    df["sv_to"] = df["sv_c"] + df["to_c"]

    (fig, ax) = figure_axes(
        title=(
            f"{date:%-d %b %Y} National Weather Service:: "
            "Storm Based Warning Load"
        ),
        subtitle="Unofficial IEM Archives, presented as a stacked bar chart",
        figsize=(8, 6),
    )

    ax.bar(
        df.index,
        df["a_c"],
        width=1 / 1440.0,
        color=NWS_COLORS["SV.W"],
        label="Severe T'Storm",
    )
    ax.bar(
        df.index,
        df["b_c"],
        width=1 / 1440.0,
        color=NWS_COLORS["TO.W"],
        label="Tornado",
    )
    ax.bar(
        df.index,
        df["ff_c"],
        width=1 / 1440.0,
        color="g",  # Eh
        label="Flash Flood",
    )
    ax.plot(
        df.index,
        df["a_c"],
        color="k",
        drawstyle="steps-post",
    )
    ax.plot(
        df.index,
        df["b_c"],
        color="k",
        drawstyle="steps-post",
    )
    ax.plot(
        df.index,
        df["ff_c"],
        color="k",
        drawstyle="steps-post",
    )

    ax.grid(True)
    ax.xaxis.set_major_locator(
        mdates.HourLocator(byhour=[0, 3, 6, 9, 12, 15, 18, 21], tz=TZ)
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I %p", tz=TZ))

    ax.set_ylabel("Total Warning Count (SVR+TOR+FFW)")
    ax.legend(loc=1, ncol=2)
    ax.set_ylim(bottom=0.1, top=df["a_c"].max() * 1.2)
    ax.set_xlim(to_t[1080], to_t[1080 + 1440])
    ax.set_xlabel("Central Daylight Time")
    ax.annotate(
        f"TOR+SVR+FFW Max: {df['a_c'].max()} @{df['a_c'].idxmax():%-I:%M %p}"
        f"\nTOR+SVR Max: {df['sv_to'].max()} @{df['sv_to'].idxmax():%-I:%M %p}"
        f"\nTOR Max: {df['to_c'].max()} @{df['to_c'].idxmax():%-I:%M %p}"
        f"\nSVR Max: {df['sv_c'].max()} @{df['sv_c'].idxmax():%-I:%M %p}"
        f"\nFFW Max: {df['ff_c'].max()} @{df['ff_c'].idxmax():%-I:%M %p}",
        xy=(0.01, 0.95),
        xycoords="axes fraction",
        bbox=dict(facecolor="white"),
        ha="left",
        va="top",
    )

    fig.savefig(f"{date:%Y%m%d}.png")


def work():
    """Our workflow"""
    events = (
        "4/27/11, 3/2/11, 4/26/11, 5/25/11, 10/26/10, 4/15/11, 1/10/08,"
        " 4/10/09, 6/11/09, 5/11/08, 5/22/11, 6/2/09, 7/22/08, 7/1/12, "
        "8/5/10, 6/9/11, 6/21/11, 5/26/11, 4/26/11, 8/2/08"
    )
    for event in events.split(","):
        print(event)
        date = datetime.datetime.strptime(event.strip(), "%m/%d/%y")
        date = date.replace(hour=12, tzinfo=ZoneInfo("UTC"))
        main(date)


if __name__ == "__main__":
    work()
