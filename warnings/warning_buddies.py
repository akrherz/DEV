"""Who do we share a warning with?"""
import sys

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot import MapPlot, plt
from pyiem.util import get_sqlalchemy_conn


def main(argv):
    """Go Main Go."""
    opt = int(argv[1])
    wfo = argv[2]
    name = argv[3]
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_sql(
            "with events as ("
            "select distinct wfo, "
            "date(issue at time zone 'UTC' + '12 hours'::interval) from "
            "warnings where phenomena = 'SV' and significance = 'W' and "
            "issue > '2001-01-01'), "
            "local as ("
            "SELECT * from events where wfo = %s) "
            "SELECT e.wfo as ewfo, l.wfo as lwfo, e.date from "
            "events e LEFT JOIN local l on (e.date = l.date) ",
            conn,
            index_col=None,
            params=(wfo,),
        )
    if opt == 2:
        data = {}
        for gwfo, gdf in df.groupby("ewfo"):
            if gwfo == wfo:
                selftotal = len(gdf.index)
                continue
            hits = len(gdf[pd.notnull(gdf["lwfo"])].index)
            total = len(gdf.index)
            data[gwfo] = hits / float(total) * 100.0
        title = (
            "Percentage of Office's SVR 1+ Warning Days(*) "
            f"Shared with NWS {name}"
        )
    elif opt == 1:
        data = {}
        gdf = df[df["lwfo"] == wfo].groupby("ewfo").count()
        selftotal = gdf.at[wfo, "lwfo"]
        gdf = gdf.drop(wfo)
        data = gdf["lwfo"] / selftotal * 100.0
        title = (
            f"Percentage of NWS {name} SVR 1+ Warning Days(*) Shared with "
            f"Other Office, {selftotal} total"
        )
    mp = MapPlot(
        sector="nws",
        title=title,
        subtitle=(
            "2001 - 27 Jun 2020, * 12z-12z 'convective days'."
            " based on unofficial IEM Archives"
        ),
    )
    # maxval = df["count"].max()
    # print(maxval)
    bins = list(range(0, 101, 10))
    bins[0] = 1.0
    cmap = plt.get_cmap("YlGnBu")
    cmap.set_under("white")
    mp.fill_cwas(
        data,
        bins=bins,
        cmap=cmap,
        spacing="proportional",
        ilabel=True,
        lblformat="%.0f%%",
        extend="min",
        units="percent",
    )
    mp.postprocess(filename=f"/tmp/warnings{opt}_{wfo}.png")


if __name__ == "__main__":
    main(sys.argv)
