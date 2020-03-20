"""simple map with counties filled"""

from pandas.io.sql import read_sql
import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt
from pyiem.util import get_dbconn
from pyiem.plot import MapPlot


def main():
    """Do Something"""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        """
        SELECT ugc, count(*) from warnings_2011 where phenomena = 'TO'
        and significance = 'A' and issue < '2011-05-18'
        GROUP by ugc ORDER by count DESC
    """,
        pgconn,
        index_col="ugc",
    )
    mp = MapPlot(
        sector="nws",
        title=(
            "1 Jan - 17 May 2011 Number of Storm Prediction Center"
            " Tornado Watches by County"
        ),
        subtitle=(
            "count by county, "
            "based on unofficial archives maintained by the "
            "IEM"
        ),
    )
    bins = list(range(0, 19, 2))
    bins[0] = 1
    print(df["count"].max())
    cmap = plt.get_cmap("plasma")
    cmap.set_under("white")
    cmap.set_over("black")
    mp.fill_ugcs(df["count"].to_dict(), bins, cmap=cmap)
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
