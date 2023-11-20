"""Make a fancy heatmap of how this YTD compares to previous years."""

import numpy as np
import requests
from tqdm import tqdm

import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.plot import figure_axes

TAKE = ["IA2110", "IA2603", "IA6389", "IA5952", "IA7161", "IA4585", "IA2724"]
TAKE.extend(["IA5198", "IA5230", "IA1354"])


def main():
    """Go Main Go."""
    nt = NetworkTable("IACLIMATE")
    # Find online stations with data at least to 1951
    stations = []
    labels = []
    for sid in nt.sts:
        if nt.sts[sid]["archive_begin"].year > 1901:
            continue
        if not nt.sts[sid]["online"]:
            continue
        if sid[2] not in ["T"] and sid not in TAKE:
            print(sid, nt.sts[sid]["name"])
            continue
        stations.append(sid)
        lon = nt.sts[sid]["lon"]
        lat = nt.sts[sid]["lat"]
        js = requests.get(
            "https://mesonet.agron.iastate.edu/api/1/usdm_bypoint.json?"
            f"sdate=2023-09-12&edate=2023-09-12&lon={lon}&lat={lat}",
            timeout=30,
        ).json()
        dd = f"  D{js['data'][0]['category']}"
        labels.append(nt.sts[sid]["name"].replace(" Area", "") + dd)

    # a 2d array to hold our data
    data = np.zeros((len(stations), 261))

    cnts = {}
    for i, sid in tqdm(enumerate(stations)):
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                """
                SELECT day, sday, year, precip from alldata_ia
                where station = %s and precip is not null and sday < '0919'
                ORDER by day ASC
            """,
                conn,
                params=(sid,),
                index_col="day",
                parse_dates="day",
            )
        for j, dt in enumerate(
            pd.date_range("2023/01/01", "2023/09/18"), start=1
        ):
            yearly = (
                df[df["sday"] >= dt.strftime("%m%d")][["year", "precip"]]
                .groupby("year")
                .sum()
            )
            minval = yearly["precip"].min()
            minyear = yearly["precip"].idxmin()
            if minyear not in cnts:
                cnts[minyear] = 0
            cnts[minyear] += 1
            d2023 = yearly.loc[2023, "precip"]
            d2012 = yearly.loc[2012, "precip"]
            d1988 = yearly.loc[1988, "precip"]
            if minval < min(d2023, d2012, d1988):
                val = 0
            elif d2023 < d2012 and d2023 < d1988:
                val = 1
            elif d2012 < d2023 and d2012 < d1988:
                val = 2
            elif d1988 < d2012 and d1988 < d2023:
                val = 3
            data[i, 261 - j] = val

    # print the years with the largest counts
    for year, cnt in sorted(cnts.items(), key=lambda x: x[1], reverse=True)[
        :10
    ]:
        print(year, cnt)

    # Make a plot
    (fig, ax) = figure_axes(
        title="Which Year was the Driest for Date to 18 September Period?",
        subtitle="Based on IEM Climodat Sites for ~1893-2023 Period",
        figsize=(8, 6),
    )
    fig.text(0.07, 0.05, "Site 11 Sept\nDrought Class Labelled")
    ax.set_position([0.27, 0.1, 0.7, 0.8])
    # create four colors to associate with the four values above
    colors = ["white", "#00ff00", "#ff0000", "#0000ff"]
    cmap = ListedColormap(colors)
    bounds = [0, 1, 2, 3, 4]
    norm = BoundaryNorm(bounds, cmap.N)

    res = ax.imshow(
        data, aspect="auto", interpolation="nearest", cmap=cmap, norm=norm
    )
    ax.set_xticks([17, 48, 79, 109, 140, 170, 201, 229, 260])
    ax.set_xticklabels(
        ["Sep", "Aug", "Jul", "Jun", "May", "Apr", "Mar", "Feb", "Jan"]
    )
    ax.set_yticks(np.arange(0, len(stations)))
    ax.set_yticklabels(labels)
    ax.set_ylim(len(stations) + 0.5, -0.5)
    ax.grid(True)
    ax.set_xlabel("Period between given date and 18 September")
    # add legend and place labels at the center of the legend boxes
    cbar = fig.colorbar(res, ticks=[0.5, 1.5, 2.5, 3.5])
    cbar.ax.set_yticklabels(["Other\nYear", "2023", "2012", "1988"])
    fig.savefig("230919.png")


if __name__ == "__main__":
    main()
