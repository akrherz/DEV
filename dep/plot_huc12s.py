"""Plot something as a huc12 map."""

import numpy as np
from sqlalchemy import text

import geopandas as gpd
from matplotlib import colors as mpcolors
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL

SQL = """
with data as (
    select huc_12,
    sum(case when extract(year from valid) = 2023 then avg_loss else 0 end)
    as loss2023,
    sum(case when extract(year from valid) = 2019 then avg_loss else 0 end)
    as loss2019
    from results_by_huc12 where scenario = 0 and
    extract(year from valid) in (2023, 2019) group by huc_12
)
    select simple_geom, h.huc_12, (loss2023 - loss2019) * 4.463 as loss
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
        title=(
            "2023 Hillslope Soil Loss minus 2019 "
            "Hillslope Soil Loss [T/a] by HUC12"
        ),
        logo="dep",
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=3,
    )
    cmap = get_cmap("PuOr_r")
    # cmap.set_bad("#000000")
    # cmap.set_over("#ffff00")
    bins = np.arange(-5, 5.1, 1.0)
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(df["loss"])),
        zorder=Z_POLITICAL,
    )
    mp.drawcounties()
    mp.draw_colorbar(bins, cmap, norm, title="tons/acre", extend="both")

    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
