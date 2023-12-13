"""Plot what we have in myhucs.csv"""

import numpy as np
from sqlalchemy import text

import geopandas as gpd
from matplotlib import colors as mpcolors
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from pyiem.util import get_sqlalchemy_conn

SQL = """
with data as (
    select huc12,
    sum(case when substr(management, 1, 1) = '1' then acres else 0 end),
    sum(acres) as total
    from fields where scenario = 0 and
    substr(landuse, 17, 1) in ('C', 'B') GROUP by huc12
)
    select simple_geom, h.huc_12, sum as no_till_acres, total
    from huc12 h LEFT JOIN data d on (h.huc_12 = d.huc12)
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
    df["percent"] = df["no_till_acres"] / df["total"] * 100.0
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
        title=(
            "13 Dec 2023 :: Percentage of 2023 Corn/Soybean Acres in No-Till"
        ),
        subtitle=(
            "Overall: "
            f"{df['no_till_acres'].sum() / df['total'].sum() * 100.0:.1f}%"
        ),
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
