"""SBW Intersection"""

import tqdm
import pandas as pd
from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable


def make_map():
    """Generate a map plot"""
    df = pd.read_csv("vertex_intersects.csv")
    gdf = df.groupby("wfo").sum()
    allvals = (gdf["allhits"] - gdf["cwahits"]) / gdf["verticies"] * 100.0
    avgv = (
        (gdf["allhits"].sum() - gdf["cwahits"].sum())
        / gdf["verticies"].sum()
        * 100.0
    )
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        title=(
            "Percent of SVR+TOR Warning Vertices within 2km "
            "of County Border"
        ),
        subtitle=(
            "1 Oct 2007 through 29 Mar 2018, "
            "Overall Avg: %.1f%%, * CWA Borders Excluded"
        )
        % (avgv,),
    )
    mp.fill_cwas(allvals.to_dict(), ilabel=True, lblformat="%.0f")
    mp.postprocess(filename="test.png")


def plot():
    """Make a plot"""
    df = pd.read_csv("vertex_intersects.csv")
    gdf = df.groupby("year").sum()
    allvals = (gdf["allhits"] - gdf["cwahits"]) / gdf["verticies"] * 100.0
    fwd = df[df["wfo"] == "FWD"]
    fwdvals = (fwd["allhits"] - fwd["cwahits"]) / fwd["verticies"] * 100.0
    (fig, ax) = plt.subplots(1, 1)
    ax.bar(allvals.index.values - 0.2, allvals.values, width=0.4, label="NWS")
    ax.bar(fwd["year"].values + 0.2, fwdvals.values, width=0.4, label="FWD")
    ax.grid(True)
    ax.set_title(
        (
            "NWS Storm Based Warning Vertex Overlapping Border\n"
            "Percentage of TOR/SVR Verticies overlapping county, not CWA"
        )
    )
    ax.legend(ncol=2)
    ax.set_ylabel("Percentage Overlapping")
    fig.text(
        0.01,
        0.01,
        (
            "@akrherz 20 Nov 2017, based on 2km "
            "buffering with US Albers EPSG:2163"
        ),
    )
    fig.savefig("test.png")


def main():
    """Go Main Go"""
    # wfo = argv[1]
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    nt = NetworkTable("WFO")

    rows = []
    for wfo in tqdm.tqdm(nt.sts):
        for year in range(2008, 2018):
            table = f"sbw_{year}"
            cursor.execute(
                f"""
            WITH dumps as (
                select (st_dumppoints(ST_Transform(geom, 2163))).* from
                {table} where wfo = %(wfo)s
                and phenomena in ('SV', 'TO')
                and status = 'NEW' and issue > '2007-10-01'),
            points as (
                SELECT path, geom from dumps),
            cbuf as (
                SELECT ugc, name,
                ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(
                    st_transform(geom, 2163)),1)),2000.) as bgeom
                from ugcs where wfo = %(wfo)s
                and substr(ugc, 3, 1) = 'C' and end_ts is null),
            wbuf as (
                SELECT wfo,
                ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(
                    st_transform(the_geom, 2163)),1)),2000.) as wgeom
                from cwa where wfo = %(wfo)s),
            agg as (
                select (path)[3] as pt, p.geom, c.name
                from points p LEFT JOIN cbuf c ON
                ST_Within(p.geom, c.bgeom) where (path)[3] != 1),
            agg2 as (
                select a.pt, a.name, c.wfo from agg a LEFT JOIN wbuf c ON
                ST_Within(a.geom, c.wgeom))

            select sum(case when name is not null then 1 else 0 end),
            sum(case when wfo is not null then 1 else 0 end), count(*)
            from agg2
            """,
                dict(wfo=wfo),
            )

            if cursor.rowcount > 0:
                row = cursor.fetchone()
                rows.append(
                    dict(
                        wfo=wfo,
                        year=year,
                        allhits=row[0],
                        cwahits=row[1],
                        verticies=row[2],
                    )
                )
    df = pd.DataFrame(rows)
    df.to_csv("vertex_intersects.csv")


if __name__ == "__main__":
    # main()
    # plot()
    make_map()
