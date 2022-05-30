"""Generic plotter"""

from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_sqlalchemy_conn
import pandas as pd


def main():
    """Go MAin"""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            """
            WITH data as (
                select distinct ugc, extract(year from issue) as year, eventid
                from warnings where phenomena = 'FF' and is_emergency
            )
            SELECT ugc, count(*) from data GROUP by ugc ORDER by count DESC
        """,
            conn,
            index_col="ugc",
        )

    bins = list(range(0, 41, 4))
    bins[0] = 1
    cmap = get_cmap("jet")
    cmap.set_over("black")
    cmap.set_under("white")
    mp = MapPlot(
        sector="state",
        state="TX",
        continentalcolor="white",
        figsize=(12.0, 9.0),
        title=("2003-2022 Flash Flood Emergency Events"),
        subtitle=("based on unofficial IEM archives, data till 30 May 2022."),
    )
    mp.fill_ugcs(
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
