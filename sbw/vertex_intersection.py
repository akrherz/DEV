"""SBW Intersection"""
from __future__ import print_function

import tqdm
import pandas as pd
import matplotlib.pyplot as plt
from pyiem.util import get_dbconn
from pyiem.network import Table as NetworkTable


def plot():
    """Make a plot"""
    df = pd.read_csv('vertex_intersects.csv')
    gdf = df.groupby('year').sum()
    allvals = (gdf['allhits'] - gdf['cwahits']) / gdf['verticies'] * 100.
    fwd = df[df['wfo'] == 'FWD']
    fwdvals = (fwd['allhits'] - fwd['cwahits']) / fwd['verticies'] * 100.
    (fig, ax) = plt.subplots(1, 1)
    ax.bar(allvals.index.values - 0.2, allvals.values, width=0.4, label='NWS')
    ax.bar(fwd['year'].values + 0.2, fwdvals.values, width=0.4, label='FWD')
    ax.grid(True)
    ax.set_title(("NWS Storm Based Warning Vertex Overlapping Border\n"
                  "Percentage of TOR/SVR Verticies overlapping county, not CWA"
                  ))
    ax.legend(ncol=2)
    ax.set_ylabel("Percentage Overlapping")
    fig.text(0.01, 0.01,
             ("@akrherz 20 Nov 2017, based on 2km "
              "buffering with US Albers EPSG:2163"))
    fig.savefig('test.png')


def main():
    """Go Main Go"""
    # wfo = argv[1]
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()

    nt = NetworkTable("WFO")

    rows = []
    for wfo in tqdm.tqdm(nt.sts):
        for year in range(2008, 2018):
            table = "sbw_%s" % (year, )
            cursor.execute("""
            WITH dumps as (
                select (st_dumppoints(ST_Transform(geom, 2163))).* from
                """ + table + """
                where wfo = %(wfo)s
                and phenomena in ('SV', 'TO')
                and status = 'NEW'),
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
            """, dict(wfo=wfo))

            if cursor.rowcount > 0:
                row = cursor.fetchone()
                rows.append(dict(
                    wfo=wfo,
                    year=year,
                    allhits=row[0],
                    cwahits=row[1],
                    verticies=row[2]
                    ))
    df = pd.DataFrame(rows)
    df.to_csv('vertex_intersects.csv')


if __name__ == '__main__':
    plot()
    # main()
