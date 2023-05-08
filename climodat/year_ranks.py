"""Create a plot to compare with NCEI."""
import os

from sqlalchemy import text
from tqdm import tqdm

import matplotlib.colors as mpcolors
import pandas as pd
from pyiem.plot import MapPlot
from pyiem.reference import state_names
from pyiem.util import get_sqlalchemy_conn


def get_data():
    """make data."""
    dfs = []
    progress = tqdm(state_names.keys())
    with get_sqlalchemy_conn("coop") as conn:
        for state in progress:
            progress.set_description(state)
            df = pd.read_sql(
                text(
                    """
                with obs as (
                    select station, year, sum(precip) from alldata WHERE
                    station = :station and year >= 1895 and
                    year < 2023 GROUP by station, year
                ), agg as (
                    select station, year, rank() OVER (PARTITION by station
                        ORDER by sum ASC) from obs
                )
                select station, rank from agg where year = 2022
                """
                ),
                conn,
                params={"station": f"{state}0000"},
                index_col=None,
            )
            if df.empty:
                continue
            dfs.append(df)
    pd.concat(dfs).to_csv("data.csv", index=False)


def main():
    """Go Main Go."""
    if not os.path.isfile("data.csv"):
        get_data()
    colors = "#8c540a #d8b365 #f6e8c3 #f7f7f7 #c7eae5 #5ab4ac #01655e".split()
    bins = [1, 2, 15, 40, 80, 113, 128, 129]
    cmap = mpcolors.ListedColormap(colors)

    df = (
        pd.read_csv("data.csv")
        .assign(state=lambda _df: _df["station"].str.slice(0, 2))
        .set_index("state")
    )
    print(df)
    mp = MapPlot(
        sector="conus",
        title="IEM Estimated 2022 Precipitation Rank (1=Driest) by State",
        subtitle="Based on unofficial IEM archives 1895-2022",
    )
    mp.fill_states(
        df["rank"].to_dict(),
        bins=bins,
        cmap=cmap,
        ilabel=True,
        units="rank",
        lblformat="%.0f",
        labelbuffer=0,
        extend="neither",
    )
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
