"""Convert the plot.out into something more usable."""

import calendar

import click
import numpy as np
import pandas as pd
from dailyerosion.reference import KG_M2_TO_TON_ACRE
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pyiem.plot import figure

DATE_AXIS = pd.date_range("2007/01/01", "2026/12/31")
VARNAMES = {
    "fl_cov%": "Fractional Flat Cover %",
    "ne_wus": "Actual Friction Velocity",
    "t_wust": "Threshold Friction Velocity",
    "wus_anemom": "Friction Velocity\nafter Anemometer Only",
    "wus_random": "Friction Velocity\nafter Random Roughness Only",
    "wus_ridge": "Friction Velocity\nafter Ridge Only",
    "wus_biodrg": "Friction Velocity\nafter Biodrag Only",
}
XWIDTH = 0.19


def add_month_labels(ax: Axes):
    """Go common things."""
    ax.set_xticks([1, 60, 121, 182, 244, 305])
    ax.set_xticklabels(calendar.month_abbr[1:][::2])


def do_friction(dailydf: pd.DataFrame, fig: Figure):
    """Do the hard work here."""
    xpos = 0.05
    xdelta = 0.24
    ymax = None
    for stepvar in ["wus_anemom", "wus_random", "wus_ridge", "wus_biodrg"]:
        ax = fig.add_axes((xpos, 0.6, XWIDTH, 0.25))
        xpos += xdelta
        ax.set_title(VARNAMES.get(stepvar, stepvar))
        ax.set_ylabel(stepvar)
        for yr in range(2007, 2027):
            yeardf = dailydf[dailydf.index.year == yr]
            ax.plot(
                yeardf["doy"],
                yeardf[stepvar].to_numpy(),
            )
        add_month_labels(ax)
        ax.grid(True)
        if ymax is None:
            ymax = ax.get_ylim()[1]
        ax.set_ylim(0, ymax)


def row2(dailydf: pd.DataFrame, fig: Figure):
    """Stuff done in row2"""

    ax1 = fig.add_axes((0.05, 0.35, XWIDTH, 0.2))
    ax1.set_title(VARNAMES["fl_cov%"])
    ax1.set_ylabel("fl_cov%")
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        ax1.plot(
            yeardf["doy"],
            yeardf["fl_cov%"].to_numpy(),
        )
    add_month_labels(ax1)
    ax1.grid(True)
    ax1.set_ylim(0, 1)

    ax1 = fig.add_axes((0.3, 0.35, XWIDTH, 0.2))
    ax1.set_title(VARNAMES["t_wust"])
    ax1.set_ylabel("t_wust")
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        ax1.plot(
            yeardf["doy"],
            yeardf["t_wust"].to_numpy(),
        )
    add_month_labels(ax1)
    ax1.grid(True)
    ax1.set_ylim(bottom=0)
    ylim = ax1.get_ylim()

    ax1 = fig.add_axes((0.55, 0.35, XWIDTH, 0.2))
    ax1.set_title(VARNAMES["ne_wus"])
    ax1.set_ylabel("ne_wus")
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        ax1.plot(
            yeardf["doy"],
            yeardf["ne_wus"].to_numpy(),
        )
    add_month_labels(ax1)
    ax1.grid(True)
    ax1.set_ylim(*ylim)

    # Compute contribution frequencies when the threshold was above the actual
    ax1 = fig.add_axes((0.75, 0.35, XWIDTH, 0.2), frame_on=False)
    ax1.set_title("Var Stops Erosion")
    ax1.set_xticks([])
    ax1.set_yticks([])
    cell_text = []
    for col in ["t_ne_bare", "t_flat_cov", "t_surf_wet", "t_ag_den", "t_wust"]:
        freq = (dailydf[col] >= dailydf["ne_wus"]).sum() / dailydf.shape[0]
        cell_text.append([col, f"{freq * 100.0:.2f}%"])
    ax1.table(
        cellText=cell_text,
        colLabels=["Variable", "Frequency"],
        loc="center",
        bbox=(0, 0, 1, 1),
    )


@click.command()
@click.option("--var1", required=True)
@click.option("--var2", required=True)
def main(var1: str, var2: str) -> None:
    """Go Main Go."""
    data = np.loadtxt("plot.out", skiprows=1)
    with open("plot.out") as fh:
        names = [
            x.strip() for x in fh.read(1000).split("\n")[0][2:].split("|")
        ]
    dailydf = pd.DataFrame(data, columns=names, index=DATE_AXIS)
    dailydf["doy"] = dailydf.index.dayofyear

    tayr = abs(dailydf["tot_loss"].sum() * KG_M2_TO_TON_ACRE / 20.0 * -1)
    events = (dailydf["tot_loss"] < 0).sum()
    fig = figure(
        title="WEPS: Real wind. Grace6, 70% Sand",
        subtitle=(
            f"Total Erosion: {tayr:.4f} tons/acre/yr over {events} events"
        ),
        logo="dep",
        figsize=(10.24, 10.24),
    )
    do_friction(dailydf, fig)
    row2(dailydf, fig)

    # Diagnose eros, which is the off on flag, I believe
    ax = fig.add_axes((0.65, 0.05, XWIDTH, 0.23))
    data = np.zeros((20, 366))
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        data[yr - 2007, : len(yeardf.index)] = yeardf["eros"].to_numpy()
    ax.imshow(data, aspect="auto", interpolation="nearest")
    ax.set_yticks(np.arange(0, 20, 5))
    ax.set_yticklabels(np.arange(2007, 2027, 5))
    ax.set_title("eros Erosion Possible? yellow=yes")
    add_month_labels(ax)
    ax.grid(True)

    # Plot var1 from command line
    ax1 = fig.add_axes((0.05, 0.05, XWIDTH, 0.23))
    ax1.set_title(VARNAMES.get(var1, var1))
    ax1.set_ylabel(var1)
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        ax1.plot(
            yeardf["doy"],
            yeardf[var1].to_numpy(),
        )
    add_month_labels(ax1)
    ax1.grid(True)

    # Plot var2 from command line
    ax1 = fig.add_axes((0.35, 0.05, XWIDTH, 0.23))
    ax1.set_title(VARNAMES.get(var2, var2))
    ax1.set_ylabel(var2)
    for yr in range(2007, 2027):
        yeardf = dailydf[dailydf.index.year == yr]
        ax1.plot(
            yeardf["doy"],
            yeardf[var2].to_numpy(),
        )
    add_month_labels(ax1)
    ax1.grid(True)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
