"""Year that was as wet as this."""

from pyiem.plot.geoplot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
import pandas as pd
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    nt = NetworkTable(["IACLIMATE", "ILCLIMATE", "INCLIMATE", "MOCLIMATE"])
    pgconn = get_dbconn("coop")
    df = read_sql(
        """
        SELECT station,
        case when month > 9 then year + 1 else year end as myyear,
        sum(precip) as total from alldata
        WHERE (month > 9 or month < 6) and
        substr(station, 3, 1) not in ('C', 'T')
        and substr(station, 3, 4) != '0000'
        and substr(station, 1, 2) in ('IA', 'IL', 'IN', 'MO')
        GROUP by station, myyear
    """,
        pgconn,
        index_col=None,
    )
    y2019 = df[df["myyear"] == 2019].set_index("station")
    lats = []
    lons = []
    vals = []
    colors = []
    for station, df2 in df.groupby("station"):
        df3 = df2[df2["total"] > y2019.at[station, "total"]]
        last = df3["myyear"].max()
        lats.append(nt.sts[station]["lat"])
        lons.append(nt.sts[station]["lon"])
        vals.append("R" if pd.isna(last) else last)
        colors.append("k" if vals[-1] != "R" else "b")
    mp = MapPlot(
        sector="iailin",
        continentalcolor="white",
        subtitle='Locations with blue "R" had the largest accumulation for period',
        title="Previous year wetter than 1 Oct 2018 - 31 May 2019",
    )
    mp.plot_values(lons, lats, vals, textsize=12, labelbuffer=1, color=colors)
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
