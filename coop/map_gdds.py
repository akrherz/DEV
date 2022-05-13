"""Map GDD totals"""

from pyiem.util import get_sqlalchemy_conn
from pyiem.plot import MapPlot
from pandas.io.sql import read_sql

# NOTE: this fancy SQL did not save much in time.
SQL = """
with freezes as (
    select station, year, min(day) as min_day from alldata WHERE
    substr(station, 3, 1) not in ('C', 'T') and substr(station, 3, 4) != '0000'
    and year >= 1992 and year < 2022 and month > 7 and low <= 28 and (
    (station > 'ND0000' and station < 'ND9999') or
    (station > 'SD0000' and station < 'SD9999') or
    (station > 'NE0000' and station < 'NE9999') or
    (station > 'KS0000' and station < 'KS9999') or
    (station > 'MO0000' and station < 'MO9999') or
    (station > 'IA0000' and station < 'IA9999') or
    (station > 'MN0000' and station < 'MN9999') or
    (station > 'WI0000' and station < 'WI9999') or
    (station > 'IL0000' and station < 'IL9999') or
    (station > 'IN0000' and station < 'IN9999') or
    (station > 'MI0000' and station < 'MI9999') or
    (station > 'OH0000' and station < 'OH9999') or
    (station > 'KY0000' and station < 'KY9999'))
    GROUP by station, year
), obs as (
    select a.station, a.year, gdd50(high, low) as gdd from alldata a, freezes f
    where a.station = f.station and a.year = f.year and a.day < f.min_day and
    a.sday >= '0520'
), agg as (
    select station, year, sum(gdd) as gdd from obs GROUP by station, year
)
    select a.*, st_x(t.geom) as lon, st_y(t.geom) as lat from agg a, stations t
    where a.station = t.id and t.network ~* 'CLIMATE'
"""


def main():
    """Go Main!"""
    with get_sqlalchemy_conn("coop") as conn:
        df = read_sql(SQL, conn, index_col="station")
    # Enforce a quorum of 30 years of data
    gdf = df.groupby(df.index).count()
    df = df.loc[gdf.loc[gdf.gdd == 30].index]
    df.to_csv("gdds.csv")
    df = df.groupby(df.index).mean()
    mp = MapPlot(
        title=(
            "1992-2021 Average Growing Degree Days(50/86) "
            "May 20 -> First Fall 28F"
        ),
        sector="midwest",
        drawstates=True,
        continentalcolor="white",
    )
    mp.contourf(
        df.lon,
        df.lat,
        df.gdd,
        clevs=range(2000, 4000, 200),
    )
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["gdd"].values,
        fmt="%.0f",
        textsize=12,
        labelbuffer=5,
        color="r",
    )
    mp.drawcounties()
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
