"""Who do we share a watch with?"""

import sys

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap


def main(argv):
    """Go Main Go."""
    wfo = argv[1]
    name = argv[2]
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            """with dmx as (
            select distinct vtec_year as year, eventid from
            warnings where phenomena = 'SV' and significance = 'A'
            and wfo = %s),
            other as (select distinct vtec_year as year,
            eventid,
            wfo from warnings where phenomena = 'SV' and significance = 'A'
            and wfo != 'HFO')
            select d.wfo, count(*) from dmx x JOIN other d
            on (x.eventid = d.eventid and x.year = d.year) GROUP by d.wfo""",
            conn,
            index_col="wfo",
            params=(wfo,),
        )
    selftotal = df.at[wfo, "count"]
    df = df.drop(wfo)
    mp = MapPlot(
        sector="nws",
        title=(
            f"NWS {name} shared Severe Thunderstorm Watch Events, "
            f"{selftotal} total"
        ),
        subtitle=(
            "1 Oct 2005 - 26 Jun 2020, a single watch event covers "
            "counties in both CWAs. based on unofficial IEM Archives"
        ),
    )
    maxval = df["count"].max()
    print(maxval)
    bins = [1, 5, 10, 25, 50, 75, 100, 150]
    cmap = get_cmap("plasma")
    mp.fill_cwas(
        df["count"],
        bins=bins,
        cmap=cmap,
        spacing="proportional",
        ilabel=True,
        extend="neither",
        units="events",
        lblformat="%.0f",
        labelbuffer=0,
    )
    mp.postprocess(filename=f"/tmp/{wfo}.png")


if __name__ == "__main__":
    main(sys.argv)
