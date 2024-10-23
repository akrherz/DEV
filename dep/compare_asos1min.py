"""Compare our DEP/WEPP breakpoint precipitation data with ASOS 1 minute."""

import datetime
import sys
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import pandas as pd
import requests
from pyiem.plot import figure
from pyiem.util import get_sqlalchemy_conn, mm2inch
from sqlalchemy import text


def main(argv):
    """Run comparison."""
    station = argv[1]
    date = datetime.datetime.strptime(argv[2], "%Y-%m-%d")
    # Get station metadata
    meta = requests.get(
        f"https://mesonet.agron.iastate.edu/api/1/station/{station}.json",
        timeout=30,
    ).json()["data"][0]
    lat = meta["latitude"]
    lon = meta["longitude"]
    # call DEP webservice to get climate file
    req = requests.get(
        "https://mesonet-dep.agron.iastate.edu"
        f"/dl/climatefile.py?lat={lat}&lon={lon}",
        timeout=30,
    )
    with open("/tmp/dep.cli", "wb") as fh:
        fh.write(req.content)

    with get_sqlalchemy_conn("asos1min") as conn:
        obs = pd.read_sql(
            text(
                """
            select valid, precip from alldata_1minute where station = :sid
            and valid >= :sts and valid < (:sts + '1 day'::interval)
            ORDER by valid asc
            """
            ),
            conn,
            params={"sid": station, "sts": date},
        )
    obs["valid"] = obs["valid"].dt.tz_convert(ZoneInfo("America/Chicago"))
    obs = obs.set_index("valid")
    with open("/tmp/dep.cli", encoding="ascii") as fh:
        lines = fh.readlines()
    last = None
    lookfor = f"{date.day}\t{date.month}\t{date.year}"
    for linenum, line in enumerate(lines):
        if not line.startswith(lookfor):
            continue
        breaks = int(line.split("\t")[3])
        for i in range(breaks):
            tokens = lines[linenum + i + 1].split()
            hr = int(float(tokens[0]))
            mi = int((float(tokens[0]) - hr) * 60.0)
            cum = float(tokens[1])
            ts = datetime.datetime(
                date.year,
                date.month,
                date.day,
                hr,
                mi,
                tzinfo=ZoneInfo("America/Chicago"),
            )
            if last is None:
                last = [ts, cum]
                continue
            # compute the rainfall rate in inch/minute
            precip = mm2inch(cum - last[1])
            preciprate = precip / ((ts - last[0]).seconds / 60.0)
            obs.at[ts, "dep"] = preciprate
            obs.at[ts, "deptot"] = precip
            last = [ts, cum]

    obs["precip"] = obs["precip"].fillna(0)
    obs["deptot"] = obs["deptot"].fillna(0)

    fig = figure(
        title=f"{date:%-d %B %Y} {meta['name']} (K{station}) Rainfall Rate",
        logo="dep",
        figsize=(8, 6),
    )
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.35])
    ax.plot(
        obs.index.values,
        obs["precip"].cumsum(),
        label=f"ASOS 1 minute: {obs['precip'].sum():.2f}",
    )
    ax.plot(
        obs.index.values,
        obs["deptot"].cumsum(),
        label=f"DEP:  {obs['deptot'].sum():.2f}",
    )
    ax.legend(loc="best")
    ax.set_ylabel("Rainfall Total [inch]")
    ax.grid(True)
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%-I:%M %p", tz=ZoneInfo("America/Chicago"))
    )

    ax = fig.add_axes([0.1, 0.5, 0.8, 0.35])
    ax.scatter(obs.index.values, obs["precip"], label="ASOS 1 minute")
    ax.scatter(obs.index.values, obs["dep"], label="DEP")
    ax.legend(loc="best")
    ax.set_ylabel("Rainfall Rate [inch / minute]")
    ax.grid(True)
    ax.set_ylim(0, 0.13)
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%-I:%M %p", tz=ZoneInfo("America/Chicago"))
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    main(sys.argv)
