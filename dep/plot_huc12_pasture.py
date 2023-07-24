"""
Investigate if we have too much pasture...
"""

from sqlalchemy import text

import geopandas as gpd
from matplotlib import colors as mpcolors
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from pyiem.util import get_sqlalchemy_conn

SQL = """
WITH ofecounts as (
    select huc_12, count(*) as ofe_count,
    sum(case when genlu = 2 then 1 else 0 end) as pasture_count from
    flowpath_ofes o, flowpaths f, fields d WHERE o.flowpath = f.fid
    and o.fbndid = d.fbndid and f.huc_12 = d.huc12 and
    f.scenario = 0 GROUP by huc_12
), flds as (
    select huc12,
    sum(case when isag then acres else 0 end) as ag_acres,
    sum(case when genlu = 2 then acres else 0 end) as pasture_acres
    from fields WHERE scenario = 0 GROUP by huc12
)

SELECT o.huc_12, o.ofe_count, o.pasture_count , f.ag_acres, f.pasture_acres,
h.simple_geom from ofecounts o, flds f, huc12 h WHERE
o.huc_12 = f.huc12 and f.huc12 = h.huc_12 and h.scenario = 0

"""


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        df = gpd.read_postgis(
            text(SQL),
            conn,
            geom_col="simple_geom",
            index_col="huc_12",
        )
    # ratio of Pasture OFEs to Pasture Acres
    df["ratio"] = (df["pasture_count"] / df["ofe_count"]) / (
        df["pasture_acres"] / df["ag_acres"]
    )
    df["ratio"] = (df["pasture_acres"] / df["ag_acres"]) * 100.0
    print(df.sort_values("ratio", ascending=False).head(5))
    minx, miny, maxx, maxy = df.to_crs(4326)["simple_geom"].total_bounds
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="custom",
        south=miny,
        north=maxy,
        west=minx,
        east=maxx,
        title=("Percentage of HUC12 ISAG Acres with Pasture Landuse"),
        logo="dep",
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=3,
    )
    cmap = get_cmap("RdBu")
    cmap.set_bad("#000000")
    cmap.set_over("#ffff00")
    # bins = [0, 0.1, 0.2, 0.5, 0.7, 1, 1.2, 1.5, 2, 3, 5]
    bins = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(df["ratio"])),
        zorder=Z_POLITICAL,
    )
    mp.draw_colorbar(bins, cmap, norm, title="Percentage", extend="max")

    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
