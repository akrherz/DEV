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
                    select huc_12, sum(qc_precip) as precip,
                    sum(avg_runoff) as runoff from results_by_huc12
                    where scenario = 0 and valid in
                    ('2023-02-26', '2023-02-27')
                    GROUP by huc_12
                )
                select simple_geom, h.huc_12, precip, runoff from huc12 h
                LEFT JOIN data d on (h.huc_12 = d.huc_12) WHERE h.scenario = 0
                """
            ),
            conn,
            geom_col="simple_geom",
            index_col="huc_12",
        )
    # df = df.fillna(0)
    df["ratio"] = df["runoff"] / df["precip"] * 100.0
    df2 = df[df["precip"] >= 5]
    minx, miny, maxx, maxy = df2.to_crs(4326)["simple_geom"].total_bounds
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="iowa",
        south=miny,
        north=maxy,
        west=minx,
        east=maxx,
        title=(
            "26-27 Feb 2023 Daily Erosion Project (DEP) "
            "Percent Runoff vs Precip"
        ),
        subtitle="for DEP HUC12s with at least 5mm of precipitation",
        logo="dep",
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=3,
    )
    cmap = get_cmap("RdBu")
    cmap.set_bad("#000000")
    cmap.set_over("#ffff00")
    bins = np.arange(0, 100.1, 10.0)
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    df2.to_crs(mp.panels[0].crs).plot(
        aspect=None,
        ax=mp.panels[0].ax,
        color=cmap(norm(df2["ratio"])),
        zorder=Z_POLITICAL,
    )
    mp.drawcounties()
    mp.draw_colorbar(bins, cmap, norm, title="Percent Runoff", extend="max")

    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
