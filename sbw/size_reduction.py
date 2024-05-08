"""Plot SBW size reduction."""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            """
        WITH polys as (
            SELECT wfo, eventid, extract(year from issue) as year,
            phenomena, ST_Area(geom::geography) / 1e6 as area from
            sbw where polygon_begin > '2019-01-01' and
            phenomena in ('TO', 'TO') and status = 'NEW'
            and significance = 'W'
        ), counties as (
            select w.wfo, extract(year from issue) as year,
            eventid, phenomena, sum(area2163) as area from warnings w
            JOIN ugcs u on (w.gid = u.gid) WHERE phenomena in ('TO', 'TO')
            and significance = 'W' and issue > '2019-01-01'
            GROUP by w.wfo, year, eventid, phenomena
        ), agg as (
            select p.wfo, p.area as polyarea, c.area as countyarea
            from polys p LEFT JOIN counties c on (p.wfo = c.wfo and
            p.year = c.year and p.eventid = c.eventid
            and p.phenomena = c.phenomena)
        )
        select wfo, 100. - sum(polyarea) / sum(countyarea) * 100. as reduction,
        sum(polyarea) as polyarea, sum(countyarea) as countyarea
        from agg group by wfo
        """,
            conn,
            index_col="wfo",
        )
    if "JSJ" in df.index and "SJU" not in df.index:
        df.loc["SJU"] = df.loc["JSJ"]

    nationwide = 100 - (df["polyarea"].sum() / df["countyarea"].sum()) * 100.0

    mp = MapPlot(
        sector="nws",
        title="Tornado Polygon Warning Size Reduction vs County %",
        subtitle=(
            "1 Jan 2019 - 7 May 2024, based on IEM archives."
            f"overall {nationwide:.1f}%"
        ),
    )
    cmap = get_cmap("jet")
    ramp = range(0, 101, 10)
    mp.fill_cwas(
        df["reduction"],
        bins=ramp,
        cmap=cmap,
        units="Percent",
        ilabel=True,
        lblformat="%.0f",
        labelbuffer=0,
        extend="neither",
    )
    mp.postprocess(filename="190101_240507_tor_size_reduction.png")


if __name__ == "__main__":
    main()
