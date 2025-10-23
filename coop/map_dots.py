"""A map of dots!"""

import os

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_OVERLAY, state_names
from tqdm import tqdm


def get_data():
    """Get data."""
    dfs = []
    progress = tqdm(state_names)
    for state in progress:
        progress.set_description(state)
        with get_sqlalchemy_conn("coop") as dbconn:
            df = pd.read_sql(
                sql_helper(
                    """
    with data as (
      select station, count(*), sum(case when high = 67 then 1 else 0 end)
      as hits
      from {table} where high is not null group by station)
    select station, st_x(geom) as lon, st_y(geom) as lat,
    hits / count::float * 100 as freq
    from stations t JOIN data d on (t.id = d.station) WHERE
    t.network ~* 'CLIMATE' and count > 50 * 365
                """,
                    table=f"alldata_{state.lower()}",
                ),
                dbconn,
                index_col="station",
            )
            dfs.append(df)
    pd.concat(dfs).to_csv("/tmp/data.csv", index=True)


def main():
    """Go Main Go."""
    if not os.path.isfile("/tmp/data.csv"):
        get_data()
    df = pd.read_csv("/tmp/data.csv").sort_values("freq", ascending=False)
    df["days"] = df["freq"] / 100.0 * 365.25
    df["state"] = df["station"].str.slice(0, 2)
    print(df[df["state"] == "HI"].head(20))
    print(df["days"].describe())
    # bins = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
    # bins = [1, 7, 21, 45, 90, 120, 180, 210, 240, 270, 300]
    cmap = get_cmap("managua")
    # norm = mpcolors.Normalize(1, 366)
    # colors = cmap(norm(df['doy'].values))

    mp = MapPlot(
        title=("Days per Year with Daily High Temperature of 67°F"),
        axisbg="white",
        subtitle=("Based on NWS COOP Sites with 50+ years data, CA"),
        sector="state",
        state="HI",
    )
    # clevlabels = calendar.month_abbr[1:] + [""]
    mp.contourf(
        df["lon"].values,
        df["lat"].values,
        df["days"].values,
        np.arange(0, 10, 1),
        cmap=cmap,
        # marker="o",
        # s=50,
        zorder=Z_OVERLAY,
        extend="max",
        spacing="proportional",
        units="days / year",
        # clevlabels=clevlabels,
    )

    mp.postprocess(filename="251021.png")


if __name__ == "__main__":
    main()
