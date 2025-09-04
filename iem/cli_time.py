"""CLI timing."""

import os
from typing import Any

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import cm
from matplotlib.colors import LogNorm
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import figure_axes


def conv_time(row: Any):
    """Figure out the time, if possible (legacy signature kept)."""
    if isinstance(row, dict):
        return conv_time_text(row.get("high_time"))
    return conv_time_text(row)


def conv_time_text(high_time: Any):
    """Figure out hour from a high_time string."""
    try:
        parts = str(high_time).split()
        hr = int(parts[0][:-2])
        # Don't care about minutes
        if parts[1] == "PM" and hr != 12:
            hr += 12
        if parts[1] == "AM" and hr == 12:
            hr = 0
        return hr
    except Exception as exp:
        # best effort; no row context here
        print(exp, high_time)
        return None


def main():
    """Go Main Go."""
    if not os.path.isfile("/tmp/cli_time.csv"):
        dump()
    df = pd.read_csv("/tmp/cli_time.csv", parse_dates=["valid"])
    # GIGO
    df = df[df["hour"] < 24]

    (fig, ax) = figure_axes(
        title="2000-2025 NWS CLImate Sites",
        subtitle="Heatmap of Hour of Daily High Temperature",
        figsize=(8, 6),
    )

    counts = pd.crosstab(df["hour"], df["valid"].dt.isocalendar().week)
    # Do not plot ISO week 53 (too few points)
    if 53 in counts.columns:
        counts = counts.drop(columns=[53])
    # Avoid LogNorm failing on zeros by masking them (they will appear blank)
    maxc = int(counts.values.max()) if counts.size else 1
    if maxc < 1:
        maxc = 1
    counts_masked = counts.replace(0, np.nan)

    norm = LogNorm(vmin=1, vmax=maxc)
    # create a discrete colormap with 10 colors from the YlGnBu palette
    cmap = cm.get_cmap("YlGnBu", 14)
    # ticks at powers of 10 up to the max count
    max_exp = int(np.ceil(np.log10(maxc))) if maxc > 0 else 0
    ticks = (10 ** np.arange(0, max_exp + 1)).tolist()

    sns.heatmap(
        counts_masked,
        cmap=cmap,
        ax=ax,
        norm=norm,
        square=False,
        cbar_kws={"label": "Count", "ticks": ticks},
    )

    # Replace isoweek axis (1-52) with approximate month labels.
    # Use the ISO week for the 15th of each month in a reference year
    cols = counts.columns.to_numpy()
    ref_year = 2020
    month_weeks = [
        pd.Timestamp(ref_year, m, 15).isocalendar().week for m in range(1, 13)
    ]
    positions = []
    labels = []
    for m, wk in enumerate(month_weeks, start=1):
        # find nearest existing week column
        if wk in cols:
            pos = int(np.where(cols == wk)[0][0])
        else:
            pos = int(np.abs(cols - wk).argmin())
        positions.append(pos)
        labels.append(pd.Timestamp(1900, m, 1).strftime("%b"))

    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=0)
    ax.set_xlabel("Partitioned by ISO Week of Year")
    ax.set_ylabel("Local Standard Time Hour")

    # Make y-axis labels friendlier and invert so Midnight is at the top
    row_hours = counts.index.to_numpy()
    y_positions = np.arange(len(row_hours))

    def hour_label(h: int) -> str:
        if h == 0:
            return "Midnight"
        if h == 12:
            return "Noon"
        if 1 <= h < 12:
            return f"{h} AM"
        return f"{h - 12} PM"

    y_labels = [hour_label(int(h)) for h in row_hours]
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, rotation=0)
    ax.invert_yaxis()
    ax.grid(True)
    fig.savefig("250904.png")


def dump():
    """Dump data."""
    with get_sqlalchemy_conn("iem") as pgconn:
        df = pd.read_sql(
            """
        SELECT valid, station, high_time
        from cli_data WHERE strpos(high_time, ' AM') > 0 or
        strpos(high_time, ' PM') > 0 ORDER by valid ASC
        """,
            pgconn,
            index_col=None,
            parse_dates=["valid"],
        )
    # apply to the high_time Series directly to get the hour
    df["hour"] = df["high_time"].apply(conv_time_text)
    df.to_csv("/tmp/cli_time.csv", index=False)


if __name__ == "__main__":
    main()
