"""Map of precipitable water"""

import numpy as np

from metpy.units import units
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main"""
    nt = NetworkTable(["AWOS", "IA_ASOS"], only_online=False)
    pgconn = get_dbconn("mos")
    df = read_sql(
        """
    select station, avg(pwater) from model_gridpoint where
    model = 'NAM' and extract(hour from runtime at time zone 'UTC') = 0
    and pwater > 0 and pwater < 100 and
    extract(month from runtime) = 1 and ftime = runtime
    GROUP by station ORDER by avg
    """,
        pgconn,
        index_col="station",
    )
    df["lat"] = None
    df["lon"] = None
    df["pwater"] = (df["avg"].values * units("mm")).to(units("inch")).m
    for station in df.index.values:
        df.at[station, "lat"] = nt.sts[station[1:]]["lat"]
        df.at[station, "lon"] = nt.sts[station[1:]]["lon"]

    mp = MapPlot(
        title=("00z Analysis NAM January Average " "Precipitable Water [in]"),
        subtitle=("based on grid point samples " "from 2004-2020 for January"),
    )
    cmap = plt.get_cmap("plasma_r")
    cmap.set_under("white")
    cmap.set_over("black")
    print(df["pwater"].describe())
    mp.contourf(
        df["lon"],
        df["lat"],
        df["pwater"],
        np.arange(0.26, 0.37, 0.02),
        cmap=cmap,
        units="inch",
    )
    mp.drawcounties()
    mp.drawcities()
    mp.postprocess(filename="200205.png")


if __name__ == "__main__":
    main()
