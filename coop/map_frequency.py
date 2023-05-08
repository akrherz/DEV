"""Map values"""

from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main!"""
    nt = NetworkTable("IACLIMATE")
    pgconn = get_dbconn("coop")

    df = read_sql(
        """
    with data as (
        select station, year, sum(precip) from alldata_ia
        WHERE sday >= '0601' and sday < '0606' and year >= 1995
        and year < 2010
        GROUP by station, year
    )
    select station, sum(case when sum >= 0.5 then 1 else 0 end) as hits,
    count(*) from data GROUP by station ORDER by station ASC
    """,
        pgconn,
        index_col="station",
    )
    df["lat"] = 0.0
    df["lon"] = 0.0
    df["freq"] = df["hits"] / df["count"] * 100.0
    for station, _ in df.iterrows():
        if station in nt.sts and station != "IA0000" and station[2] != "C":
            df.at[station, "lat"] = nt.sts[station]["lat"]
            df.at[station, "lon"] = nt.sts[station]["lon"]

    mp = MapPlot(
        title="1-5 June :: Frequency of +0.5 inches of Precipitation",
        subtitle="based on 1995-2019 data",
        sector="state",
        state="IA",
        drawstates=True,
        continentalcolor="white",
    )
    df2 = df[df["lat"] > 20]
    cmap = plt.get_cmap("terrain_r")
    mp.contourf(
        df2["lon"].values,
        df2["lat"].values,
        df2["freq"].values,
        range(0, 101, 10),
        extend="neither",
        units="Frequency [%]",
        cmap=cmap,
    )
    mp.plot_values(
        df2["lon"].values, df2["lat"].values, df2["freq"].values, fmt="%.0f%%"
    )
    mp.drawcounties()
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
