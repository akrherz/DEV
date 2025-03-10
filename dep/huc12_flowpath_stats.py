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
        )
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
        title="HUC12 median / mean soil delivery [ratio]",
        logo="dep",
        caption="Daily Erosion Project",
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

    clevs = np.arange(0.3, 1.3, 0.1)
    cmap = get_cmap("plasma")
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
        extend="max",
    )

    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
