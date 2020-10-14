"""Map cli_data"""

from pyiem.util import get_dbconn
from pyiem.plot import MapPlot
from pandas.io.sql import read_sql


def main():
    """Map some CLI data"""
    pgconn = get_dbconn("iem")

    df = read_sql(
        """
    WITH data as (
        SELECT station, snow_jul1 - snow_jul1_normal as s
        from cli_data where valid = '2019-02-18' and snow_jul1 > 0
        and snow_jul1_normal > 0)

    select station, st_x(geom) as lon, st_y(geom) as lat, c.s as val from
    data c JOIN stations s on (s.id = c.station)
    WHERE s.network = 'NWSCLI'
    """,
        pgconn,
        index_col=None,
    )
    df["color"] = "#ff0000"
    df.loc[df["val"] > 0, "color"] = "#0000ff"

    mp = MapPlot(
        sector="midwest",
        axisbg="white",
        title="2018-2019 Snowfall Total Departure from Average [inches]",
        subtitle="18 Feb 2019 Based on NWS CLI Reporting Sites",
    )
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["val"].values,
        fmt="%.1f",
        textsize=12,
        color=df["color"].values,
        labelbuffer=1,
    )
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
