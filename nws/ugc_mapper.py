"""simple map with counties filled"""

import geopandas as gpd
from matplotlib import colors as mpcolors
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_FILL


def main():
    """Do Something"""
    with get_sqlalchemy_conn("postgis") as pgconn:
        df = gpd.read_postgis(
            """
            with data as (
                SELECT ugc, count(*) from warnings where phenomena = 'BZ'
                and significance = 'W' GROUP by ugc ORDER by count DESC
            ), agg as (
                select d.ugc, simple_geom, count,
                 rank() OVER (PARTITION by d.ugc ORDER by u.end_ts DESC)
                 from ugcs u JOIN data d on
                (u.ugc = d.ugc) ORDER by count ASC
            )
            select * from agg where rank = 1
        """,
            pgconn,
            index_col="ugc",
            geom_col="simple_geom",
        )
    mp = MapPlot(
        sector="nws",
        title=(
            "12 Nov 2005 - 25 Oct 2023 Number of NWS Issued Blizzard Warnings"
        ),
        subtitle=(
            "count by county/zone, "
            "based on unofficial archives maintained by the "
            "IEM"
        ),
    )

    bins = [1, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
    cmap = get_cmap("jet")
    cmap.set_under("white")
    cmap.set_over("black")
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    for panel in mp.panels:
        df.to_crs(panel.crs).plot(
            ax=panel.ax,
            aspect=None,
            fc=cmap(norm(df["count"].to_numpy())),
            ec="k",
            lw=0.1,
            zorder=Z_FILL,
        )
    mp.draw_colorbar(bins, cmap, norm, extend="max", spacing="proportional")
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
