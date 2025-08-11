"""Attempt a viz ideas."""

import geopandas as gpd
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import EPSG, Z_OVERLAY2


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        huc12df = gpd.read_postgis(
            sql_helper("""
    select ST_x(ST_centroid(geom)) as x, ST_y(ST_centroid(geom)) as y,
    huc_12, simple_geom from huc12 where scenario = 0"""),
            conn,
            index_col="huc_12",
            geom_col="simple_geom",
        )  # type: ignore
    huc12df["outside"] = np.nan

    minx, miny, maxx, maxy = huc12df.total_bounds
    buffer = 10_000
    mp = MapPlot(
        apctx={"_r": "43"},
        sector="custom",
        projection=EPSG[5070],
        south=miny - buffer,
        north=maxy + buffer,
        west=minx + buffer,
        east=maxx - buffer,
        title="DEP Ratio of median to mean soil delivery by HUC12",
        subtitle="Computed over 2007-2024",
        logo=None,
        nocaption=True,
        continentalcolor="white",
        stateborderwidth=1,
    )

    for huc12, _row in huc12df.iterrows():
        df = pd.read_csv(
            f"/i/0/ofe/{huc12[:8]}/{huc12[8:]}/fpresults_{huc12}.csv"
        )
        data = df["delivery[t/a/yr]"].to_numpy()
        # figure out the percentage of flowpaths outside of 2 sigma
        mu = np.mean(data)
        huc12df.at[huc12, "outside"] = np.median(data) / mu

    print(huc12df["outside"].describe())

    clevs = np.arange(0.1, 1.11, 0.2)
    cmap = get_cmap("RdYlBu")
    cmap.set_bad("None")
    norm = BoundaryNorm(clevs, cmap.N)

    huc12df[huc12df["outside"] >= 0].plot(
        ax=mp.panels[0].ax,
        zorder=Z_OVERLAY2,
        color=cmap(norm(huc12df["outside"].to_numpy())),
    )
    mp.draw_colorbar(
        clevs,
        cmap,
        norm,
        extend="both",
    )

    mp.fig.savefig("figure2.png", dpi=300)


if __name__ == "__main__":
    main()
