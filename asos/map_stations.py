"""map of dates."""

from datetime import timedelta
from zoneinfo import ZoneInfo

import numpy as np
from sqlalchemy import text

import pandas as pd
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_sqlalchemy_conn


def run(dt):
    """Run for this time."""
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                """
            select station, st_x(geom), st_y(geom), max(valid) from t2023 a,
            stations t where t.id = a.station and t.network ~* 'ASOS'
            and array_to_string(wxcodes, '') LIKE '%%FU%%'
            and valid > :sts and valid <= :ets
            GROUP by station, st_x, st_y order by max desc
            """
            ),
            conn,
            params={"sts": dt - timedelta(hours=4), "ets": dt},
            index_col="station",
        )
    mp = MapPlot(
        sector="north_america",
        continentalcolor="black",
        title="METAR Smoke Reports (Code: FU)",
        subtitle=f"Within four hour window ending {dt:%d %b %Y %I %p} CDT",
        statebordercolor="white",
        stateborderwidth=0.5,
    )
    if not df.empty:
        df["secs"] = (dt - df["max"]).dt.total_seconds()
        mp.scatter(
            df["st_x"].values,
            df["st_y"].values,
            df["secs"].values,
            np.arange(0, 3600 * 4, 600),
            cmap=get_cmap("Greys"),
            draw_colorbar=False,
        )
    return mp


def main():
    """Go Main Go."""
    i = 0
    for dt in pd.date_range(
        "2023/05/01",
        "2023/07/06 09:00",
        freq="1H",
        tz=ZoneInfo("America/Chicago"),
    ):
        print(dt)
        mp = run(dt)
        mp.fig.savefig(f"frames/frame{i:04.0f}.png")
        mp.close()
        i += 1


if __name__ == "__main__":
    main()
