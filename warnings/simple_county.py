"""Map UGC stuff."""

from pandas.io.sql import read_sql
import numpy as np
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")

    cmap = get_cmap("terrain")
    cmap.set_over("red")

    mp = MapPlot(
        sector="conus",
        axisbg="#EEEEEE",
        title=(
            "Percentage of All Tornado Watches for Location "
            "Active at 3 AM CDT (8 UTC)"
        ),
        subtitle=("Based on unofficial IEM archives (2005-2021)"),
        cwas=True,
        twitter=True,
    )

    # norm = mpcolors.BoundaryNorm(bins, cmap.N)

    df = read_sql(
        """
    with events as (select ugc, generate_series(issue at time zone 'UTC',
    expire at time zone 'UTC', '1 minute'::interval) as ts from warnings
    where phenomena = 'TO' and significance = 'A'), totals as (select ugc,
    count(*) from warnings where phenomena = 'TO' and significance = 'A'
    GROUP by ugc), morning as (select ugc, count(*) from events where
    extract(hour from ts) = 8 and extract(minute from ts) = 0 GROUP by ugc)
    select t.ugc, t.count as events, m.count as morning
    from totals t LEFT JOIN morning m on
    (t.ugc = m.ugc)
    """,
        pgconn,
        index_col="ugc",
    )
    df = df.fillna(0)
    df["percent"] = df["morning"] / df["events"] * 100.0
    print(df["percent"].max())
    mp.fill_ugcs(
        df["percent"].to_dict(),
        bins=[0, 0.1, 5, 10, 15, 20, 25, 30, 35, 40],
        cmap=cmap,
        units="%",
        spacing="uniform",
        extend="max",
    )
    mp.draw_cwas()
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
