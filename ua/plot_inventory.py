"""A heatmap of RAOB inventory."""

import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("raob") as conn:
        reports = pd.read_sql(
            sql_helper("""
    select station, valid from raob_flights where
    valid >= '2025-01-01 00:00+00' and substr(station, 1, 1) in ('K', 'P')
    and extract(hour from valid at time zone 'UTC') in (0, 12) and
    valid < '2025-05-17 00:00+00' and station not in ('KEDW', 'KNID', 'KDPG',
    'KVPS', 'KLMN')
    order by station asc, valid asc
                       """),
            conn,
            index_col=None,
        )

    fig = figure(
        subtitle="Based on NCEI IGRA2 data processed by the IEM",
        title="00 + 12 UTC US Sounding Reports, 1 Jan - 16 May 2025",
        figsize=(8, 8),
    )
    ax = fig.add_axes((0.1, 0.25, 0.85, 0.65))
    hasdata = np.zeros(
        (reports["station"].nunique(), reports["valid"].nunique()), dtype=int
    )
    stations = reports["station"].unique().tolist()
    stations.sort()
    valids = reports["valid"].unique().tolist()
    valids.sort()
    for _, row in reports.iterrows():
        i = stations.index(row["station"])
        j = valids.index(row["valid"])
        hasdata[i, j] = 1

    # Create custom colormap for binary data (0=red, 1=green)
    colors = ["red", "green"]
    cmap = ListedColormap(colors)

    ax.imshow(
        hasdata,
        aspect="auto",
        interpolation="nearest",
        origin="lower",
        extent=(-0.5, len(valids) - 0.5, -0.5, len(stations) - 0.5),
        cmap=cmap,
        vmin=0,
        vmax=1,
    )
    yticks = []
    ytickslabels = []
    quorum = len(valids) * 0.9
    for i, station in enumerate(stations):
        labeli = i
        if yticks and yticks[-1] == labeli - 1:
            labeli += 1
        if len(reports[reports["station"] == station].index) < quorum:
            yticks.append(labeli)
            ytickslabels.append(station)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ytickslabels)
    ax.set_ylabel(r"Station, Coverage < 90% labelled")

    xticks = []
    xtickslabels = []
    for i, valid in enumerate(valids):
        if valid.hour == 0 and valid.day == 1:
            xticks.append(i)
            xtickslabels.append(valid.strftime("%-d %b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtickslabels)
    ax.grid(axis="x")

    # Add x-axis counts
    ax = fig.add_axes((0.1, 0.05, 0.85, 0.15))
    ax.set_ylabel("Sites Per Launch")
    gdf = reports.groupby("valid").count()
    ax.bar(
        range(len(gdf.index)),
        gdf["station"],
        width=1,
        color="blue",
    )
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtickslabels)
    ax.grid(True)
    ax.set_xlim(-0.5, len(valids) - 0.5)
    ax.set_ylim(60, 90)

    fig.savefig("inventory.png")


if __name__ == "__main__":
    main()
