"""Map UGC stuff."""

import subprocess
import sys

import pytz
from pandas.io.sql import read_sql
from pyiem.database import get_dbconn
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import utc


def main(argv):
    """Go Main Go."""
    hr = int(argv[1])
    valid = utc(2021, 7, 7, hr).astimezone(pytz.timezone("America/Chicago"))
    pgconn = get_dbconn("postgis")

    cmap = get_cmap("jet")
    # cmap.set_over("purple")

    mp = MapPlot(
        sector="conus",
        axisbg="#EEEEEE",
        title=(
            "Percentage of All Tornado Watches for Location "
            "Active at %s CDT (%s UTC)" % (valid.strftime("%-I %p"), hr)
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
    extract(hour from ts) = %s and extract(minute from ts) = 0 GROUP by ugc)
    select t.ugc, t.count as events, m.count as morning
    from totals t LEFT JOIN morning m on
    (t.ugc = m.ugc)
    """,
        pgconn,
        params=(hr,),
        index_col="ugc",
    )
    df = df.fillna(0)
    df["percent"] = df["morning"] / df["events"] * 100.0
    print(df["percent"].max())
    mp.fill_ugcs(
        df["percent"].to_dict(),
        bins=[0, 0.1, 5, 10, 20, 30, 40, 50, 60, 70, 80],
        cmap=cmap,
        units="%",
        spacing="uniform",
        extend="max",
    )
    mp.draw_cwas()
    i = hr - 12 if hr >= 12 else hr + 12
    mp.fig.savefig(f"frame_{i:02.0f}.png")
    subprocess.call(
        ["convert", f"frame_{i:02.0f}.png", f"frame_{i:02.0f}.gif"]
    )


if __name__ == "__main__":
    main(sys.argv)
