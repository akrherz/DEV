"""Map of pressure fluctation."""
from datetime import timedelta, timezone

import matplotlib.colors as mpcolors
from matplotlib.colorbar import ColorbarBase
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql
from geopandas import read_postgis
import pandas as pd
import numpy as np


def main():
    """Go Main Go."""
    pgconn = get_dbconn("asos1min")
    frame = 0

    cmap = get_cmap("RdBu")
    norm = mpcolors.BoundaryNorm(np.arange(-0.1, 0.11, 0.02), 256)
    minutes = 15
    for dt in pd.date_range(
        "2022-01-15 11:30", "2022-01-15 19:00", freq="60S"
    ).tz_localize(timezone.utc):
        df = read_postgis(
            """
            with data as (
                select station, valid at time zone 'UTC' as valid,
                pres1 from t202201_1minute where
                valid > %s and valid <= %s and pres1 is not null
                ORDER by station, valid
            )
            select station, valid, pres1, geom from data JOIN stations on
            (data.station = stations.id) WHERE stations.network ~* 'ASOS'
            """,
            pgconn,
            index_col=None,
            geom_col="geom",
            params=(dt - timedelta(minutes=minutes), dt),
        )
        mp = MapPlot(
            sector="conus",
            continentalcolor="k",
            statebordercolor="white",
            title=f"{minutes} Minute Pressure Altimeter Sparkline ending at {dt:%b %d %Y %H%M} UTC",
            subtitle=f"Data via NCEI/NWS One Minute ASOS, colored by {minutes} minute change",
        )
        xmin, xmax = mp.panels[0].ax.get_xlim()
        psz = (xmax - xmin) * 0.02
        df = df.to_crs(mp.panels[0].crs)
        for _station, gdf in df.groupby("station"):
            # Create a little spark line for each station, with a color based
            # on the pressure change
            x0 = gdf.iloc[0]["geom"].x - psz / 2.0
            y0 = gdf.iloc[0]["geom"].y
            # x0 is anchored to the left
            xpos = (
                x0
                + (gdf["valid"] - gdf["valid"].values[0]).dt.total_seconds()
                / (minutes * 60)
                * psz
            )
            # y is anchored to the last point, which is the current value
            ypos = y0 + (gdf["pres1"] - gdf["pres1"].values[-1]) / 0.05 * psz
            mp.panels[0].ax.plot(
                xpos,
                ypos,
                color=cmap(
                    norm(gdf["pres1"].values[-1] - gdf["pres1"].values[0])
                ),
                lw=2,
            )

        ncb = ColorbarBase(
            mp.cax,
            norm=norm,
            cmap=cmap,
            extend="both",
            spacing="uniform",
        )
        ncb.ax.tick_params(labelsize=8)
        ncb.set_label(
            "Altimeter Change (inHg)",
        )

        mp.postprocess(filename=f"frames/{frame:05d}.png")
        mp.close()
        frame += 1


if __name__ == "__main__":
    main()
