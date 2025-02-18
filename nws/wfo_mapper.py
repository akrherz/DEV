"""Generic plotter"""

import sys

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap


def get_database_data(year):
    """Get data from database"""
    with get_sqlalchemy_conn("postgis") as pgconn:
        df = pd.read_sql(
            """
            with data as (
    select wfo, eventid, extract(year from polygon_begin) as year,
    max(case when tornadotag = 'POSSIBLE' then 1 else 0 end) as hit
    from sbw where phenomena = 'SV' and polygon_begin > '2015-01-01'
    and status = 'NEW' group by wfo, eventid, year )
    select wfo, sum(hit) as hits,
    count(*), sum(hit) / count(*)::float * 100. as freq
    from data WHERE year = %s GROUP by wfo ORDER by wfo asc
        """,
            pgconn,
            index_col="wfo",
            params=(year,),
        )
    return df


def main(argv):
    """Go Main"""
    year = int(argv[1])
    df = get_database_data(year)
    print(df["freq"].describe())
    if "JSJ" in df.index:
        df.loc["SJU", "freq"] = df.loc["JSJ", "freq"]

    bins = np.arange(0, 41, 5)
    # bins = [1, 2, 5, 10, 20, 30, 50, 75, 100, 125, 150, 175]
    # bins = [-50, -25, -10, -5, 0, 5, 10, 25, 50]
    # bins[0] = 1
    # clevlabels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    cmap = get_cmap("YlOrRd")
    freq = df["hits"].sum() / df["count"].sum() * 100.0
    extra = "till 1 Jun 2022" if year == 2022 else ""
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        figsize=(12.0, 9.0),
        title=(
            f"{year} Percentage of Svr TStorm Warnings (at issuance) "
            "with Tornado 'POSSIBLE' Tag"
        ),
        subtitle=(
            f"{extra}, based on unofficial IEM Archives. Overall: "
            f"{df['hits'].sum():,.0f}/{df['count'].sum():,.0f} {freq:.1f}%"
        ),
    )
    mp.fill_cwas(
        df["freq"],
        bins=bins,
        lblformat="%.1f",
        cmap=cmap,
        ilabel=True,  # clevlabels=clevlabels,
        units="%",
        labelbuffer=0,
        extend="neither",
    )

    mp.postprocess(filename=f"{year}_SVR_torpossible.png")


if __name__ == "__main__":
    main(sys.argv)
