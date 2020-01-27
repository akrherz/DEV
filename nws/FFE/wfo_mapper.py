"""Generic plotter"""

from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go MAin"""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        """
        WITH data as (
            select distinct wfo, extract(year from issue) as year, eventid
            from warnings where phenomena = 'FF' and is_emergency
            and issue < '2020-01-01'
        )
        SELECT wfo, count(*) from data GROUP by wfo ORDER by count DESC
    """,
        pgconn,
        index_col="wfo",
    )
    if "JSJ" in df.index:
        df.at["SJU", "count"] = df.at["JSJ", "count"]

    bins = list(range(0, 37, 6))
    bins[0] = 1
    cmap = plt.get_cmap("plasma_r")
    cmap.set_over("black")
    cmap.set_under("white")
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        figsize=(12.0, 9.0),
        title=("2003-2019 Flash Flood Emergency Events"),
        subtitle=(
            "based on unofficial IEM archives, searching "
            '"FFS", "FLW", "FFS".'
        ),
    )
    mp.fill_cwas(
        df["count"].to_dict(),
        bins=bins,
        lblformat="%.0f",
        cmap=cmap,
        ilabel=True,  # clevlabels=month_abbr[1:],
        units="count",
    )
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
