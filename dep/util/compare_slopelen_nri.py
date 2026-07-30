"""Plot a comparison of DEP slope length and NRI."""

import geopandas as gpd
import numpy as np
from matplotlib import colors as mpcolors
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_OVERLAY2


def main():
    """Go Main Go."""
    # we have NRI by township
    with get_sqlalchemy_conn("wepp") as conn:
        idep1 = gpd.read_postgis(
            """
            with data as (
                select avg(len) * 0.3048 as len_m, model_twp
                from nri group by model_twp
            )
            select st_transform(the_geom, 5070) as geom, d.model_twp,
            d.len_m from data d JOIN iatwp i on (d.model_twp = i.model_twp)
            """,
            conn,
            geom_col="geom",
            index_col="model_twp",
        )

    # Get all of DEP slope lengths
    with get_sqlalchemy_conn("idep") as conn:
        dep = gpd.read_postgis(
            """
            select f.geom, real_length, fid from flowpaths f, huc12 h
            where f.scenario = 0 and f.huc_12 = h.huc_12 and h.scenario = 0
            and h.states ~* 'IA'
        """,
            conn,
            geom_col="geom",
            index_col="fid",
        )

    idep1["avg_real_length"] = (
        gpd.sjoin(idep1, dep).groupby("model_twp")["real_length"].mean()
    )
    idep1["diff"] = idep1["avg_real_length"] - idep1["len_m"]

    ll = (idep1["diff"] > 0).sum() / len(idep1) * 100.0
    mp = MapPlot(
        title="DEP Average Hillslope Length minus NRI Township Average",
        subtitle=(
            f"DEP longer: {ll:.1f}%, bias: {idep1['diff'].mean():.1f}m, "
            f"NRI Avg: {idep1['len_m'].mean():.1f}m, "
            f"DEP Avg: {idep1['avg_real_length'].mean():.1f}m"
        ),
        logo="dep",
        caption="Daily Erosion Project",
    )
    cmap = get_cmap("RdBu")
    bins = np.arange(-100, 100.1, 20.0)
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    idep1.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(idep1["diff"])),
        zorder=Z_OVERLAY2,
    )
    mp.draw_colorbar(bins, cmap, norm, units="m", extend="neither")
    mp.drawcounties()
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
