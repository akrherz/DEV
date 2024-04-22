"""We have something from NRI to compare with."""

import numpy as np

import geopandas as gpd
import matplotlib.colors as mpcolors
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_OVERLAY2


def main():
    """Go Main."""
    # Get DEP by huc12
    with get_sqlalchemy_conn("idep") as conn:
        idep = gpd.read_postgis(
            """
            with data as (
                select huc_12, sum(avg_loss) * 4.463 / 10. as loss
                from results_by_huc12
                where scenario = 0 and valid > '2008-01-01' and
                valid < '2018-01-01' GROUP by huc_12)
            select d.huc_12, d.loss, ST_Transform(simple_geom, 4326) as geo
            from data d JOIN huc12 h on (d.huc_12 = h.huc_12) WHERE
            h.scenario = 0 and h.states ~* 'IA'
            """,
            conn,
            geom_col="geo",
            index_col="huc_12",
        )
    # Get counties so that we can later join
    with get_sqlalchemy_conn("postgis") as conn:
        counties = gpd.read_postgis(
            "select simple_geom, ugc from ugcs where substr(ugc, 3, 1) = 'C' "
            "and state = 'IA' and end_ts is null",
            conn,
            geom_col="simple_geom",
            index_col=None,
        )
    counties["cfips"] = counties["ugc"].str.slice(3, 6).astype(int)
    counties = counties.set_index("cfips")
    # Get NRI
    nri = pd.read_excel(
        "/home/akrherz/Downloads/NRI_County_Q1.xlsx",
    )
    nri.columns = [
        "state",
        "sfips",
        "county",
        "cfips",
        "year",
        "erosion",
        "se",
        "me",
        "cnt",
    ]

    counties["nri"] = (
        nri[nri["state"] == "Iowa"][["cfips", "erosion"]]
        .groupby("cfips")
        .mean()
    )

    counties["dep"] = (
        gpd.sjoin(counties, idep, predicate="intersects")
        .groupby("cfips")["loss"]
        .mean()
    )

    mp = MapPlot(
        title=(
            "2008-2017 DEP County Average Erosion minus "
            "NRI County Average Erosion"
        ),
        subtitle=(
            f"NRI Avg: {counties['nri'].mean():.1f} T/a/yr, "
            f"DEP Avg: {counties['dep'].mean():.1f} T/a/yr"
        ),
        logo="dep",
        caption="Daily Erosion Project",
    )
    cmap = get_cmap("RdBu")
    bins = np.arange(-5, 5.1, 1.0)
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    counties["diff"] = counties["dep"] - counties["nri"]
    counties.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(counties["diff"])),
        zorder=Z_OVERLAY2,
    )
    mp.plot_values(
        counties.centroid.x,
        counties.centroid.y,
        counties["diff"].values,
        fmt="%.1f",
        labelbuffer=0,
    )

    mp.draw_colorbar(bins, cmap, norm, units="T/a/yr", extend="both")
    mp.drawcounties()
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
