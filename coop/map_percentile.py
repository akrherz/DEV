"""Map values"""

from pyiem.util import get_dbconn
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql


def main():
    """Go Main!"""
    nt = NetworkTable("IACLIMATE")
    pgconn = get_dbconn("coop")

    df = read_sql(
        """
    with monthly as (
        select station, year, month, avg((high+low)/2.) from alldata_ia
        WHERE day < '2018-06-01' and high is not null
        GROUP by station, year, month),
    agg as (
        select station, year, month, avg,
        lag(avg) OVER (PARTITION by station ORDER by year ASC, month ASC)
        from monthly),
    agg2 as (
        select station, year, month, avg, lag, avg - lag as val,
        rank() OVER (PARTITION by station ORDER by avg - lag DESC)
        from agg WHERE lag is not null)
    select * from agg2 where rank = 1 ORDER by station
    """,
        pgconn,
        index_col="station",
    )
    df["lat"] = 0.0
    df["lon"] = 0.0
    for station, _ in df.iterrows():
        if station in nt.sts and station != "IA0000" and station[2] != "C":
            df.at[station, "lat"] = nt.sts[station]["lat"]
            df.at[station, "lon"] = nt.sts[station]["lon"]

    mp = MapPlot(
        title="Largest Positive Change in Month to Month Average Temperature",
        subtitle="values in red set record for April to May 2018",
        sector="state",
        state="IA",
        drawstates=True,
        continentalcolor="white",
    )
    df2 = df[df["year"] == 2018]
    mp.plot_values(
        df2["lon"].values,
        df2["lat"].values,
        df2["val"].values,
        fmt="%.1f",
        textsize=12,
        labelbuffer=5,
        color="r",
    )
    df2 = df[df["year"] != 2018]
    mp.plot_values(
        df2["lon"].values,
        df2["lat"].values,
        df2["val"].values,
        fmt="%.1f",
        textsize=12,
        labelbuffer=5,
        color="b",
    )
    mp.drawcounties()
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
