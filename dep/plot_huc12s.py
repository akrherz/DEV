"""Plot something as a huc12 map."""

import geopandas as gpd
import numpy as np
from matplotlib import colors as mpcolors
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from sqlalchemy import text

SQL = """
with data as (
    select huc_12,
    sum(case when extract(year from valid) = 2008 then qc_precip else 0 end)
    as precip2008,
    sum(case when extract(year from valid) = 2012 then qc_precip else 0 end)
    as precip2012
    from results_by_huc12 where scenario = 0 and
    extract(year from valid) in (2012, 2008) group by huc_12
)
    select simple_geom, h.huc_12, (precip2008 - precip2012) / 25.4 as loss
    from huc12 h LEFT JOIN data d on (h.huc_12 = d.huc_12)
    WHERE h.scenario = 0 and h.states ~* 'IA'
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
    # print(df)
    # df["percent"] = df["no_till_acres"] / df["total"] * 100.0
    # df = df.fillna(0)
    # df["ratio"] = df["runoff"] / df["precip"] * 100.0
    # df2 = df[df["precip"] >= 5]
    minx, miny, maxx, maxy = df.to_crs(4326)["simple_geom"].total_bounds
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="custom",
        south=miny,
        north=maxy,
        west=minx,
        east=maxx,
        title=("2008 Precipitation minus 2012 Precipitation [inch] by HUC12"),
        logo="dep",
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=3,
    )
    cmap = get_cmap("RdBu")
    # cmap.set_bad("#000000")
    # cmap.set_over("#ffff00")
    bins = np.arange(-20, 20.1, 4.0)
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(df["loss"])),
        zorder=Z_POLITICAL,
    )
    mp.drawcounties()
    mp.draw_colorbar(bins, cmap, norm, title="inch", extend="both")

    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
