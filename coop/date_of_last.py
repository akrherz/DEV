"""map of dates."""

import pandas as pd
from pyiem.plot import MapPlot
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            WITH today as (
                SELECT station, low from alldata_ia WHERE
                day = '2023-06-12'),
            last_date as (
                select a.station, max(day) from alldata_ia a, today t WHERE
                a.station = t.station and a.month = 6 and a.day < '2023-06-12'
                and a.low <= t.low GROUP by a.station
            ),
            agg as (
                select l.station, t.low, l.max as max_date from last_date l
                JOIN today t on (l.station = t.station)
            )

            SELECT a.*, st_x(geom) as lon, st_y(geom) as lat
            from agg a JOIN stations t ON
            (a.station = t.id) WHERE t.online and t.network = 'IACLIMATE'
            ORDER by max_date ASC
            """,
            conn,
            index_col="station",
            parse_dates="max_date",
        )
    df["year"] = df["max_date"].dt.year
    df["label"] = df[["low", "year"]].apply(
        lambda x: "\n".join(x.astype(str)), axis=1
    )
    df["color"] = "k"
    df.loc[df["year"] < 2003, "color"] = "b"
    df.loc[df["year"] < 1983, "color"] = "r"
    m = MapPlot(
        continentalcolor="white",
        title="12 June 2013 Low Temp"
        r"$^\circ$F"
        " and Year of Last June Low as Cold",
        subtitle=(
            "Based on NWS Long Term COOP sites, "
            "colors signify 20+ (blue) or 40+ (red) years"
        ),
    )
    m.plot_values(
        df["lon"],
        df["lat"],
        df["label"].values,
        color=df["color"].values,
        fmt="%s",
        labelbuffer=1,
        textsize=12,
    )
    m.drawcounties()
    m.postprocess(filename="230613.png")


if __name__ == "__main__":
    main()
