"""map of dates."""

from pandas.io.sql import read_sql
from pyiem.plot import MapPlot
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_sql(
            """
            SELECT id, st_x(geom) as lon, st_y(geom) as lat from stations
            WHERE network ~* 'ASOS' and archive_begin < '1979-01-01' and
            archive_end is null ORDER by id ASC
            """,
            conn,
            index_col="id",
        )
    df["val"] = "x"

    m = MapPlot(
        sector="midwest",
        continentalcolor="white",
        title="Airport Weather Stations with Data Since at Least 1979",
    )
    m.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["val"].values,
        fmt="%s",
        color="red",
        labelbuffer=1,
    )
    # m.drawcounties()
    m.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
