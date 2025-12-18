"""Scatter plot between IEMRE and ASOS."""

import httpx
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes
from tqdm import tqdm


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("iem") as pgconn:
        df = pd.read_sql(
            "SELECT id, max_tmpf, st_x(geom) as lon, st_y(geom) as lat from "
            "summary_2025 s JOIN stations t on (s.iemid = t.iemid) WHERE "
            "s.day = '2025-12-17' and t.network = 'IA_ASOS' "
            "ORDER by id asc",
            pgconn,
            index_col="id",
        )
    df["snowd"] = 0.0
    progress = tqdm(df.iterrows(), total=len(df.index))
    for sid, row in progress:
        progress.set_description(sid)
        uri = (
            "https://mesonet.agron.iastate.edu/iemre/daily/2025-12-17/"
            f"{row['lat']}/{row['lon']}/json"
        )
        data = httpx.get(uri, timeout=30).json()
        value = data["data"][0]["snowd_12z_in"]
        if value < 0.2:
            value = 0.0
        df.at[sid, "snowd"] = value

    (fig, ax) = figure_axes(
        title="17 December 2025 ASOS High Temperature vs Morning Snow Depth",
        subtitle="ASOS sites labelled by station identifier",
        figsize=(8, 6),
    )
    ax.scatter(df["snowd"], df["max_tmpf"])
    for sid, row in df[
        (df["max_tmpf"] >= 68) | (df["max_tmpf"] < 62)
    ].iterrows():
        ax.text(
            row["snowd"], row["max_tmpf"] + 0.2, sid, ha="center", rotation=45
        )
    ax.set_xlabel("IEMRE Estimated Morning Snow Depth [inches]")
    ax.set_ylabel("Observed Iowa ASOS High [°F]")
    ax.grid(True)
    fig.savefig("251218.png")


if __name__ == "__main__":
    main()
