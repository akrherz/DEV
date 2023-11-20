"""Map of pressure fluctation."""
from datetime import timedelta, timezone

import numpy as np

import matplotlib.colors as mpcolors
import pandas as pd
from geopandas import read_postgis
from matplotlib.colorbar import ColorbarBase
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_POLITICAL
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("asos")
    frame = 0

    cmap = get_cmap("RdBu")
    norm = mpcolors.BoundaryNorm(np.arange(-0.1, 0.11, 0.02), 256)

    for dt in pd.date_range(
        "2022-01-15 11:00", "2022-01-15 17:00", freq="300S"
    ).tz_localize(timezone.utc):
        df = read_postgis(
            """
            with now as (
                select station, alti from t2022 where valid = %s
                and alti is not null
            ), past as (
                select station, alti from t2022 where valid = %s
                and alti is not null
            ), agg as (
                select case when substr(n.station, 1, 1) = 'K'
                then substr(n.station, 1, 3) else n.station end as stid,
                n.alti - p.alti as delta from now n, past p
                where n.station = p.station
            )
            select id, delta, geom
            from agg JOIN stations on (agg.stid = stations.id) WHERE
            stations.network ~* 'ASOS'
            """,
            pgconn,
            index_col="id",
            geom_col="geom",
            params=(dt, dt - timedelta(minutes=15)),
        )
        colors = cmap(norm(df["delta"]))

        m = MapPlot(
            sector="conus",
            continentalcolor="white",
            twitter=True,
            title=(
                "15 Minute Pressure Altimeter Change "
                f"at {dt:%b %d %Y %H%M} UTC"
            ),
            subtitle="Data via NWS/MADIS",
        )
        df = df.to_crs(m.panels[0].crs)
        m.panels[0].ax.scatter(
            df["geom"].x, df["geom"].y, c=colors, s=40, zorder=Z_POLITICAL
        )
        ncb = ColorbarBase(
            m.cax, norm=norm, cmap=cmap, extend="both", spacing="uniform"
        )
        ncb.set_label(
            "Altimeter Change (inHg)",
        )

        m.postprocess(filename=f"frames/{frame:05d}.png")
        m.close()
        frame += 1


if __name__ == "__main__":
    main()
