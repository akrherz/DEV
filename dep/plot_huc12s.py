"""Plot something as a huc12 map."""

import geopandas as gpd
import numpy as np
from matplotlib import colors as mpcolors
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL

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
        huc12df = gpd.read_postgis(
            sql_helper(
                """
with hucs as (
    select huc_12, simple_geom from huc12 where scenario = 0
), agg as (
    select huc_12, sum(case when qc_precip > 10 then 1 else 0 end) / 18 as days
    from results_by_huc12 where scenario = 0 and valid < '2025-01-01' and
    to_char(valid, 'MMDD') between '0415' and '0531'
    group by huc_12
)
    select h.huc_12, simple_geom, days from hucs h JOIN agg a on
    (h.huc_12 = a.huc_12)
                """
            ),
            conn,
            geom_col="simple_geom",
            index_col="huc_12",
        )  # type: ignore
    # datadf = pd.read_csv(
    #    "/tmp/huc12_stddev_rfactor.csv",
    #    index_col="huc_12",
    #    dtype={"huc_12": str},
    # )
    # avgdf = pd.read_csv(
    #    "/tmp/huc12_rfactor.csv", index_col="huc_12", dtype={"huc_12": str}
    # )
    # huc12df["data"] = datadf["stddev"] / avgdf["avg"]
    # print(df)
    # df["percent"] = df["no_till_acres"] / df["total"] * 100.0
    # df = df.fillna(0)
    # df["ratio"] = df["runoff"] / df["precip"] * 100.0
    # df2 = df[df["precip"] >= 5]
    minx, miny, maxx, maxy = huc12df.to_crs(4326)["simple_geom"].total_bounds
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="custom",
        south=miny,
        north=maxy,
        west=minx,
        east=maxx,
        title=("2007-2024 Calendar days with >= 10mm precipitation by HUC12"),
        subtitle="Between 15 April and 31 May",
        logo="dep",
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=3,
    )
    cmap = get_cmap("managua")
    # cmap.set_bad("#000000")
    # cmap.set_over("#ffff00")
    bins = np.arange(0, 10.1, 2)
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    huc12df.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(huc12df["days"])),
        zorder=Z_POLITICAL,
    )
    # mp.drawcounties()
    mp.draw_colorbar(bins, cmap, norm, title="days pear year", extend="max")

    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
