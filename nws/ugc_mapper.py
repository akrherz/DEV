"""simple map with counties filled"""

import cartopy.feature as cfeature
from pyiem.plot import maue, Z_POLITICAL
from pyiem.util import get_dbconn
from pyiem.plot import MapPlot
from pandas.io.sql import read_sql


def main():
    """Do Something"""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        """
        SELECT ugc, count(*) from warnings where phenomena = 'BZ'
        and significance = 'W' and issue < '2020-07-01'
        GROUP by ugc ORDER by count DESC
    """,
        pgconn,
        index_col="ugc",
    )
    mp = MapPlot(
        sector="nws",
        title=(
            "12 Nov 2005 - 1 Jul 2020 Number of NWS Issued Blizzard Warnings"
        ),
        subtitle=(
            "count by county, "
            "based on unofficial archives maintained by the "
            "IEM"
        ),
    )
    mp.ax.add_feature(cfeature.STATES, lw=1.0, zorder=Z_POLITICAL)

    bins = [1, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
    print(df["count"].max())
    cmap = maue()
    cmap.set_under("white")
    cmap.set_over("black")
    mp.fill_ugcs(
        df["count"].to_dict(),
        bins,
        cmap=cmap,
        spacing="proportional",
        plotmissing=False,
    )
    mp.fig.savefig("test.pdf")


if __name__ == "__main__":
    main()
