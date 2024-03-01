"""Map of pressure fluctation."""

from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
from tqdm import tqdm

import matplotlib.colors as mpcolors
import pandas as pd
from geopandas import read_postgis
from matplotlib.colorbar import ColorbarBase
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from pyiem.util import get_sqlalchemy_conn

CST = ZoneInfo("America/Chicago")


def place_legend(mp, x, y, xsize, ymax):
    """A cartoon helper."""
    mp.ax.plot([x, x + xsize], [y, y], color="white", lw=2, zorder=100)
    mp.ax.plot([x, x], [y, y + xsize], color="white", lw=2, zorder=100)
    mp.ax.text(
        x, y - xsize * 0.15, "15 minutes", va="top", fontsize=9, color="white"
    )
    mp.ax.text(
        x - xsize * 0.15,
        y,
        f"+/- {ymax:.02f} inHg",
        color="white",
        ha="right",
        fontsize=9,
        rotation=90,
    )


def main():
    """Go Main Go."""
    frame = 0

    cmap = get_cmap("RdBu")
    minutes = 15
    ymax = 0.20
    norm = mpcolors.BoundaryNorm(np.arange(0 - ymax, ymax + 0.001, 0.02), 256)
    progress = tqdm(
        pd.date_range(
            "2022-03-18 15:00", "2022-03-18 20:00", freq="60S"
        ).tz_localize(timezone.utc)
    )
    for dt in progress:
        progress.set_description(dt.strftime("%Y-%m-%d %H:%M"))
        with get_sqlalchemy_conn("asos1min") as conn:
            df = read_postgis(
                """
                with data as (
                    select station, valid at time zone 'UTC' as valid,
                    pres1 from t202203_1minute where
                    valid > %s and valid <= %s and pres1 is not null
                    ORDER by station, valid
                )
                select station, valid, pres1, geom from data JOIN stations on
                (data.station = stations.id) WHERE stations.network ~* 'ASOS'
                """,
                conn,
                index_col=None,
                geom_col="geom",
                params=(dt - timedelta(minutes=minutes), dt),
            )
        localdt = (
            dt.to_pydatetime().astimezone(CST).strftime("%b %d %Y %-I:%M %p")
        )
        mp = MapPlot(
            sector="southeast",
            continentalcolor="k",
            statebordercolor="white",
            title=(
                f"{minutes} Minute Pressure Altimeter Sparkline ending "
                f"at {dt:%b %d %Y %H%M} UTC"
            ),
            subtitle=(
                f"Data via NCEI/NWS One Minute ASOS, colored by {minutes} "
                f"minute change, {localdt} US Central"
            ),
        )
        xmin, xmax = mp.panels[0].ax.get_xlim()
        yn, yx = mp.panels[0].ax.get_ylim()
        psz = (xmax - xmin) * 0.02
        place_legend(
            mp, xmin + (xmax - xmin) * 0.05, yn + (yx - yn) * 0.05, psz, ymax
        )
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
                color="k",
                lw=3,
                zorder=Z_POLITICAL + 3,
            )
            mp.panels[0].ax.plot(
                xpos,
                ypos,
                color=cmap(
                    norm(gdf["pres1"].values[-1] - gdf["pres1"].values[0])
                ),
                lw=2,
                zorder=Z_POLITICAL + 4,
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
        mp.overlay_nexrad(dt, caxpos=[-0.5, -0.5, 0.1, 0.1])
        mp.postprocess(filename=f"frames/{frame:05d}.png")
        mp.close()
        frame += 1


if __name__ == "__main__":
    main()
