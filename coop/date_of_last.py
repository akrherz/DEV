"""map of dates."""

from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    nt = NetworkTable("IACLIMATE")
    pgconn = get_dbconn("coop")

    lats = []
    lons = []
    vals = []

    df = read_sql(
        """WITH today as (
        SELECT station, low from alldata_ia WHERE
        day = '2019-11-12')

        SELECT a.station, max(a.day), min(t.low) as low
        from alldata_ia a JOIN today t ON
        (a.station = t.station) WHERE a.day < '2019-11-12' and
        sday < '1113' and sday > '0701' and a.low <= t.low
        GROUP by a.station ORDER by max ASC
        """,
        pgconn,
        index_col="station",
    )

    colors = []
    for station, row in df.iterrows():
        lats.append(nt.sts[station]["lat"])
        lons.append(nt.sts[station]["lon"])
        label = "%s\n%s" % (row["low"], row["max"].year)
        vals.append(label)
        colors.append("k")

    m = MapPlot(
        continentalcolor="white",
        title="12 Nov 2019 Iowa COOP Low Temperature",
        subtitle=(
            "and most recent year with as cold a temperature "
            "prior to 13 November"
        ),
    )
    m.plot_values(
        lons, lats, vals, fmt="%s", color=colors, labelbuffer=3, textsize=12
    )
    m.drawcounties()
    m.postprocess(filename="191113.png")


if __name__ == "__main__":
    main()
