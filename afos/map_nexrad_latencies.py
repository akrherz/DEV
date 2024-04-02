"""The 2 April 2024 Outage debacle."""

from sqlalchemy import text
from tqdm import tqdm

import pandas as pd
from geopandas import read_postgis
from matplotlib.colors import BoundaryNorm, ListedColormap
from pandas.io.sql import read_sql
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.nws.vtec import NWS_COLORS
from pyiem.plot import MapPlot


def plot(nt, ts, i, sbw2):
    """Generate a plot at this timestamp."""
    with get_sqlalchemy_conn("id3b") as conn:
        latency = read_sql(
            text("""
            select substr(awips_id, 4, 3) as nexrad,
            max(wmo_valid_at) as max_valid from ldm_product_log where
            valid_at < :ts and valid_at > :ts2 and
            substr(awips_id, 1, 3) = 'N0B' GROUP by nexrad
            ORDER by max_valid DESC
            """),
            conn,
            params={"ts": ts, "ts2": ts - pd.Timedelta("3 hours")},
        )
    latency["latency"] = (ts - latency["max_valid"]).dt.total_seconds() / 60.0
    latency["lon"] = latency["nexrad"].apply(lambda x: nt.sts[x]["lon"])
    latency["lat"] = latency["nexrad"].apply(lambda x: nt.sts[x]["lat"])
    latency.loc[latency["latency"] < 0]["latency"] = 0

    mp = MapPlot(
        sector="nws",
        title=(
            "IEM Estimated NEXRAD III Latency during 2 April 2024 NWS "
            "Network Outage"
        ),
        subtitle=(
            f"{ts:%H%MZ %d %b %Y} Based on NOAAPort N0B receipt. "
            "Active Storm Based Warnings Overlaid."
        ),
    )
    # Create a rgba with 6 colors from a green (online) to red (offline)
    colors = [
        "darkgreen",
        "lightgreen",
        "orange",
    ]
    cmap = ListedColormap(colors)
    cmap.set_under("white")
    cmap.set_over("red")
    levels = [0, 15, 30, 60]
    norm = BoundaryNorm(levels, cmap.N)
    latency["color"] = [cmap(norm(x)) for x in latency["latency"].values]

    mp.plot_values(
        latency["lon"],
        latency["lat"],
        latency["nexrad"],
        fmt="%s",
        color=latency["color"],
        outlinecolor=latency["color"],
        textoutlinewidth=0,
        labelbuffer=0,
        textsize=10,
    )
    if not sbw2.empty:
        sbw2.to_crs(mp.panels[0].crs).plot(
            ax=mp.ax,
            facecolor="None",
            edgecolor=sbw2["color"],
            lw=2,
            aspect=None,
            zorder=1000,
        )

    mp.draw_colorbar(
        levels,
        cmap,
        norm,
        spacing="proportional",
        title="Latency Minutes",
        extend="max",
    )
    mp.fig.savefig(f"frames/{i:05.0f}.png")
    mp.close()


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        sbw = read_postgis(
            """
            select geom, polygon_begin, polygon_end, phenomena from sbw
            where phenomena in ('TO', 'SV', 'FF') and significance ='W'
            and polygon_begin > '2024-04-02' and polygon_begin < '2024-04-03'
            """,
            conn,
            geom_col="geom",
        )
    sbw["color"] = sbw["phenomena"].apply(lambda x: NWS_COLORS[f"{x}.W"])
    nt = NetworkTable("NEXRAD")
    progress = tqdm(
        pd.date_range(
            "2024-04-02T08:30+00", "2024-04-02T10:30+00", freq="2min"
        )
    )
    for i, ts in enumerate(progress, start=90):
        progress.set_description(str(ts))
        sbw2 = sbw[(sbw["polygon_begin"] <= ts) & (sbw["polygon_end"] >= ts)]
        plot(nt, ts, i, sbw2)


if __name__ == "__main__":
    main()
