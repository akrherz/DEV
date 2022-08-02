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
            SELECT station, max(day) as last_date from alldata_ia WHERE
            high >= 100 GROUP by station)

            SELECT a.station, last_date, st_x(geom) as lon, st_y(geom) as lat
            from today a JOIN stations t ON
            (a.station = t.id) WHERE t.online and t.network = 'IACLIMATE'
            ORDER by last_date ASC
            """,
            conn,
            index_col="station",
            parse_dates="last_date",
        )
    df["year"] = df["last_date"].dt.year
    m = MapPlot(
        continentalcolor="white",
        title="Year of Last 100+" r"$^\circ$F" "High Temperature",
        subtitle="Based on NWS Long Term COOP sites",
    )
    m.plot_values(
        df["lon"],
        df["lat"],
        df["year"].values,
        fmt="%s",
        labelbuffer=3,
        textsize=12,
    )
    m.drawcounties()
    m.postprocess(filename="220802.png")


if __name__ == "__main__":
    main()
