"""consec days"""
import datetime
from io import StringIO

import requests
from tqdm import tqdm
from pyiem.reference import state_names
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot, get_cmap
import pandas as pd


def todate(val):
    """Return a datestamp."""
    ts = datetime.date(2000, 1, 1) + datetime.timedelta(days=val - 1)
    return ts.strftime("%-m/%-d")


def plot():
    """Make the plot already."""
    df = pd.read_csv("data.csv", index_col="station")
    df["spring"] = df["min_jday"].apply(todate)
    df["fall"] = df["max_jday"].apply(todate)
    mp = MapPlot(
        twitter=True,
        sector="conus",
        title=(
            "High Temperature with ~180 days between average first spring and "
            "last fall date"
        ),
        subtitle="Based on longterm / threaded climate sites, IEM unofficial",
    )
    cmap = get_cmap("afmhot_r")
    levels = range(60, 101, 5)
    clevlabels = []
    for i in levels:
        dt = datetime.date(2000, 1, 1) + datetime.timedelta(days=i - 1)
        clevlabels.append(dt.strftime("%-m/%-d"))
    mp.contourf(
        df["lon"].values,
        df["lat"].values,
        df["tmpf"].values,
        levels,
        cmap=cmap,
        units="degrees F",
        # clevlabels=clevlabels,
    )
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["tmpf"].values,
        labelbuffer=5,
        fmt="%.0f",
    )
    mp.postprocess(filename="test.png")


def run_station(station, lon, lat):
    """Run for a station."""
    url = (
        "https://mesonet.agron.iastate.edu/plotting/auto/plot/77/network:"
        f"{station[:2]}CLIMATE::station:{station}.csv"
    )
    sio = StringIO()
    sio.write(requests.get(url).content.decode("ascii"))
    sio.seek(0)
    df = pd.read_csv(sio)
    df["days"] = df["max_jday"] - df["min_jday"]
    df2 = df[df["days"] < 180]
    return dict(
        station=station,
        tmpf=df2["tmpf"].min(),
        min_jday=df2.iloc[0]["min_jday"],
        max_jday=df2.iloc[0]["max_jday"],
        lon=lon,
        lat=lat,
    )


def main():
    """Go Main Go"""
    progress = tqdm(state_names)
    rows = []
    for state in progress:
        progress.set_description(state)
        nt = NetworkTable(f"{state}CLIMATE")
        for station in nt.sts:
            if station[2] != "T":
                continue
            rows.append(
                run_station(
                    station, nt.sts[station]["lon"], nt.sts[station]["lat"]
                )
            )
    df = pd.DataFrame(rows)
    df.to_csv("data.csv", index=False)


if __name__ == "__main__":
    # main()
    plot()
