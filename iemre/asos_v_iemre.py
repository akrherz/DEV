"""Scatter plot between IEMRE and ASOS."""

import pandas as pd
import requests
from pyiem.plot.use_agg import plt
from pyiem.util import get_sqlalchemy_conn
from tqdm import tqdm


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("iem") as pgconn:
        df = pd.read_sql(
            "SELECT id, max_tmpf, st_x(geom) as lon, st_y(geom) as lat from "
            "summary_2020 s JOIN stations t on (s.iemid = t.iemid) WHERE "
            "s.day = '2020-05-20' and t.network in ('IA_ASOS', 'AWOS') "
            "ORDER by id asc",
            pgconn,
            index_col="id",
        )
    df["srad"] = 0
    progress = tqdm(df.iterrows(), total=len(df.index))
    for sid, row in progress:
        progress.set_description(sid)
        uri = (
            "https://mesonet.agron.iastate.edu/iemre/daily/2020-05-20/"
            f"{row['lat']}/{row['lon']}/json"
        )
        data = requests.get(uri, timeout=30).json()
        df.at[sid, "srad"] = data["data"][0]["srad_mj"]

    (fig, ax) = plt.subplots(1, 1)
    ax.scatter(df["srad"], df["max_tmpf"])
    for sid, row in df[
        (df["max_tmpf"] >= 68) | (df["max_tmpf"] < 62)
    ].iterrows():
        ax.text(
            row["srad"], row["max_tmpf"] + 0.2, sid, ha="center", rotation=45
        )
    ax.set_title(
        "20 May 2020 High Temperature vs Solar Radiation\n"
        "Selected ASOS/AWOS sites labeled by site id"
    )
    ax.set_xlabel("IEMRE Estimated Solar Radiation [MJ]")
    ax.set_ylabel(r"Observed Iowa ASOS/AWOS High [$^\circ$F]")
    ax.grid(True)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
