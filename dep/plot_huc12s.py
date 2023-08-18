"""Plot what we have in myhucs.csv"""

import numpy as np
from sqlalchemy import text

from geopandas import read_postgis
from matplotlib import colors as mpcolors
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        df = read_postgis(
            text(
                """
                with data as (
                    select huc12, sum(case when
                    management = '11111111111111111' then acres else 0 end)
                    , sum(acres) as total
                    from fields where
                    scenario = 0 and isag group by huc12
                )
                select simple_geom, h.huc_12, sum / total * 100 as percent
                from huc12 h
                LEFT JOIN data d on (h.huc_12 = d.huc12) WHERE h.scenario = 0
                """
            ),
            conn,
            geom_col="simple_geom",
            index_col="huc_12",
        )
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
        title=("17 Aug 2023 :: Percentage of isAG acres in No-Till by HUC12"),
        # subtitle="for DEP HUC12s with at least 5mm of precipitation",
        logo="dep",
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=3,
    )
    cmap = get_cmap("jet")
    cmap.set_bad("#000000")
    cmap.set_over("#ffff00")
    bins = np.arange(0, 100.1, 20.0)
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(df["percent"])),
        zorder=Z_POLITICAL,
    )
    mp.drawcounties()
    mp.draw_colorbar(bins, cmap, norm, title="percent", extend="neither")

    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
